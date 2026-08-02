"""On-device memory: an episodic log plus durable notes.

Design constraints that come straight from the research:

* **It lives on the wearer's device.** A lifelog is the most sensitive data
  class this system touches. It is a local SQLite file, it is never uploaded
  wholesale, and only the few snippets a recall actually matches are sent to the
  model as context.
* **It stores text, not media.** Recording your life as video costs on the order
  of a terabyte a year and creates a permanent liability for everyone who walks
  past you. Text summaries of interactions are ~4 MB/year and are enough to
  answer "where did I leave my keys" and "what did I agree to on Tuesday".
* **Bystanders are not subjects.** Nothing about an unenrolled person is
  written here; see policy.PROHIBITIONS["persistent_bystander_profile"].

Search is SQLite FTS5 keyword matching, with a LIKE fallback for builds without
it. That is deliberately unglamorous: for a corpus of one person's own notes,
keyword recall is fast, debuggable, needs no embedding model on the critical
path, and fails in ways a user can understand and correct.
"""

from __future__ import annotations

import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from .types import Turn

_SCHEMA = """
CREATE TABLE IF NOT EXISTS turns (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts        REAL NOT NULL,
    trigger   TEXT NOT NULL,
    prompt    TEXT NOT NULL,
    reply     TEXT NOT NULL,
    saw_frame INTEGER NOT NULL DEFAULT 0,
    tools     TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS notes (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    ts      REAL NOT NULL,
    topic   TEXT NOT NULL,
    body    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_turns_ts ON turns(ts);
CREATE INDEX IF NOT EXISTS idx_notes_topic ON notes(topic);
"""

_FTS = """
CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(
    body, kind UNINDEXED, ref UNINDEXED, ts UNINDEXED
);
"""


@dataclass(frozen=True)
class Recollection:
    kind: str  # "turn" | "note"
    body: str
    ts: float

    def age_phrase(self, now: float | None = None) -> str:
        now = time.time() if now is None else now
        secs = max(0.0, now - self.ts)
        if secs < 90:
            return "just now"
        mins = secs / 60
        if mins < 90:
            return f"{int(mins)} minutes ago"
        hours = mins / 60
        if hours < 36:
            return f"{int(hours)} hours ago"
        return f"{int(hours / 24)} days ago"


#: Words too common to narrow anything down. Kept short on purpose: an
#: aggressive stop list is how a memory search starts losing real queries.
_STOPWORDS = frozenset(
    "a an and are as at be but by for from had has have i if in is it its me my "
    "of on or that the this to was were what when where which who with you your".split()
)


def _tokenize(text: str) -> list[str]:
    """Split a query into search terms.

    Two-character tokens are kept. An earlier version required three or more,
    which quietly made the memory unable to find people: "MJ", "Ed", and every
    two-letter initialism dropped out of the query entirely and the search
    returned nothing rather than failing visibly.
    """
    words = re.split(r"[^\w']+", text.lower())
    return [w for w in words if len(w) > 1 and w not in _STOPWORDS]


class Memory:
    """SQLite-backed episodic memory. Safe to use from a single event loop."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self.path)
        self._db.row_factory = sqlite3.Row
        self._db.executescript(_SCHEMA)
        try:
            self._db.executescript(_FTS)
            self._fts = True
        except sqlite3.OperationalError:  # pragma: no cover - build-dependent
            self._fts = False
        self._db.commit()

    def close(self) -> None:
        self._db.close()

    # -- writing ---------------------------------------------------------

    def record_turn(self, turn: Turn) -> int:
        cur = self._db.execute(
            "INSERT INTO turns (ts, trigger, prompt, reply, saw_frame, tools)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                time.time(),
                turn.trigger,
                turn.prompt,
                turn.reply,
                int(turn.saw_frame),
                ",".join(turn.tools_used),
            ),
        )
        rowid = int(cur.lastrowid or 0)
        self._index(f"{turn.prompt}\n{turn.reply}", "turn", rowid)
        self._db.commit()
        return rowid

    def remember(self, topic: str, body: str) -> int:
        """Store a durable fact the wearer explicitly asked to keep."""
        cur = self._db.execute(
            "INSERT INTO notes (ts, topic, body) VALUES (?, ?, ?)",
            (time.time(), topic.strip(), body.strip()),
        )
        rowid = int(cur.lastrowid or 0)
        self._index(f"{topic}\n{body}", "note", rowid)
        self._db.commit()
        return rowid

    def _index(self, body: str, kind: str, ref: int) -> None:
        if not self._fts:
            return
        self._db.execute(
            "INSERT INTO search (body, kind, ref, ts) VALUES (?, ?, ?, ?)",
            (body, kind, ref, time.time()),
        )

    # -- reading ---------------------------------------------------------

    def recall(self, query: str, limit: int = 5) -> list[Recollection]:
        terms = _tokenize(query)
        if not terms:
            return []
        if self._fts:
            try:
                match = " OR ".join(f'"{t}"' for t in terms)
                rows = self._db.execute(
                    "SELECT body, kind, ts FROM search WHERE search MATCH ?"
                    " ORDER BY rank LIMIT ?",
                    (match, limit),
                ).fetchall()
                return [
                    Recollection(kind=r["kind"], body=r["body"], ts=float(r["ts"]))
                    for r in rows
                ]
            except sqlite3.OperationalError:  # pragma: no cover
                pass
        return self._recall_fallback(terms, limit)

    def _recall_fallback(self, terms: list[str], limit: int) -> list[Recollection]:
        scored: list[tuple[int, Recollection]] = []
        rows = self._db.execute(
            "SELECT prompt, reply, ts FROM turns ORDER BY ts DESC LIMIT 500"
        ).fetchall()
        for r in rows:
            body = f"{r['prompt']}\n{r['reply']}"
            score = sum(1 for t in terms if t in body.lower())
            if score:
                scored.append((score, Recollection("turn", body, float(r["ts"]))))
        rows = self._db.execute(
            "SELECT topic, body, ts FROM notes ORDER BY ts DESC LIMIT 500"
        ).fetchall()
        for r in rows:
            body = f"{r['topic']}: {r['body']}"
            score = sum(1 for t in terms if t in body.lower())
            if score:
                scored.append((score, Recollection("note", body, float(r["ts"]))))
        scored.sort(key=lambda p: (-p[0], -p[1].ts))
        return [rec for _, rec in scored[:limit]]

    def recent_turns(self, limit: int = 6) -> list[Turn]:
        rows = self._db.execute(
            "SELECT * FROM turns ORDER BY ts DESC LIMIT ?", (limit,)
        ).fetchall()
        out = []
        for r in reversed(rows):
            out.append(
                Turn(
                    prompt=r["prompt"],
                    reply=r["reply"],
                    trigger=r["trigger"],
                    saw_frame=bool(r["saw_frame"]),
                    tools_used=tuple(t for t in r["tools"].split(",") if t),
                    ts=float(r["ts"]),
                )
            )
        return out

    def stats(self) -> dict[str, int]:
        turns = self._db.execute("SELECT COUNT(*) c FROM turns").fetchone()["c"]
        notes = self._db.execute("SELECT COUNT(*) c FROM notes").fetchone()["c"]
        return {"turns": int(turns), "notes": int(notes)}
