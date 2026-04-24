"""
db.py — SQLite helpers for the NRCan Article Scraper web app.

Tables:
  seen      — cross-run URL deduplication (pre-existing)
  runs      — one row per scrape job
  articles  — scraped article results

All functions open/close their own connection so they are safe to call
from any thread.
"""

import hashlib
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# DATA_DIR is set to /data on Render (persistent disk); falls back to cwd locally.
_DATA_DIR = Path(os.environ.get("DATA_DIR", "."))
DB_PATH   = str(_DATA_DIR / "seen_articles.db")


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS seen (
    url_hash TEXT PRIMARY KEY,
    url      TEXT,
    seen_at  TEXT
);

CREATE TABLE IF NOT EXISTS runs (
    run_id         TEXT PRIMARY KEY,
    started_at     TEXT NOT NULL,
    finished_at    TEXT,
    status         TEXT NOT NULL DEFAULT 'running',
    total_sources  INTEGER DEFAULT 0,
    sources_done   INTEGER DEFAULT 0,
    articles_found INTEGER DEFAULT 0,
    error_msg      TEXT
);

CREATE TABLE IF NOT EXISTS articles (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id     TEXT NOT NULL REFERENCES runs(run_id),
    url_hash   TEXT NOT NULL,
    title      TEXT NOT NULL,
    url        TEXT NOT NULL,
    source     TEXT NOT NULL,
    category   TEXT NOT NULL,
    published  TEXT,
    summary    TEXT,
    scraped_at TEXT NOT NULL,
    UNIQUE(url_hash, run_id)
);

CREATE INDEX IF NOT EXISTS idx_articles_run    ON articles(run_id);
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_cat    ON articles(category);
"""


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(_SCHEMA)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _hash(url: str) -> str:
    return hashlib.sha256(url.strip().encode()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Seen-URL deduplication (shared with CLI scraper)
# ---------------------------------------------------------------------------

def is_seen(url: str) -> bool:
    with _connect() as conn:
        return conn.execute(
            "SELECT 1 FROM seen WHERE url_hash=?", (_hash(url),)
        ).fetchone() is not None


def mark_seen(url: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO seen (url_hash, url, seen_at) VALUES (?,?,?)",
            (_hash(url), url, _now()),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------

def create_run(run_id: str, total_sources: int) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO runs (run_id, started_at, status, total_sources) VALUES (?,?,?,?)",
            (run_id, _now(), "running", total_sources),
        )
        conn.commit()


def update_run_progress(run_id: str, sources_done: int) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE runs SET sources_done=? WHERE run_id=?",
            (sources_done, run_id),
        )
        conn.commit()


def finish_run(run_id: str, articles_found: int) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE runs SET status='done', finished_at=?, articles_found=? WHERE run_id=?",
            (_now(), articles_found, run_id),
        )
        conn.commit()


def fail_run(run_id: str, error_msg: str) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE runs SET status='error', finished_at=?, error_msg=? WHERE run_id=?",
            (_now(), error_msg[:1000], run_id),
        )
        conn.commit()


def get_run(run_id: str) -> Optional[dict]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        return dict(row) if row else None


def get_runs(limit: int = 20) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM runs ORDER BY started_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_latest_run_id() -> Optional[str]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT run_id FROM runs WHERE status='done' ORDER BY finished_at DESC LIMIT 1"
        ).fetchone()
        return row["run_id"] if row else None


# ---------------------------------------------------------------------------
# Articles
# ---------------------------------------------------------------------------

def insert_articles(run_id: str, rows: list[dict]) -> int:
    if not rows:
        return 0
    records = [
        (
            run_id,
            _hash(r["URL"]),
            r["Title"],
            r["URL"],
            r["Source"],
            r["Category"],
            r.get("Published", ""),
            r.get("Summary", ""),
            r.get("Scraped At", _now()),
        )
        for r in rows
    ]
    with _connect() as conn:
        conn.executemany(
            """INSERT OR IGNORE INTO articles
               (run_id, url_hash, title, url, source, category, published, summary, scraped_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            records,
        )
        conn.commit()
    return len(records)


def get_articles(
    run_id: str,
    category: str = "",
    source: str = "",
    q: str = "",
) -> list[dict]:
    sql = "SELECT * FROM articles WHERE run_id=?"
    params: list = [run_id]

    if category:
        sql += " AND category=?"
        params.append(category)
    if source:
        sql += " AND source=?"
        params.append(source)
    if q:
        sql += " AND (title LIKE ? OR summary LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])

    sql += " ORDER BY published DESC, id DESC"

    with _connect() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def get_distinct_values(run_id: str, column: str) -> list[str]:
    allowed = {"category", "source"}
    if column not in allowed:
        return []
    with _connect() as conn:
        rows = conn.execute(
            f"SELECT DISTINCT {column} FROM articles WHERE run_id=? ORDER BY {column}",
            (run_id,),
        ).fetchall()
        return [r[0] for r in rows]
