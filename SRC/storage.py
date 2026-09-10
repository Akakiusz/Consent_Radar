"""Stage 2: SQLite persistence — read/write captured domains."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

import config

@contextmanager
def _connect():
    conn = sqlite3.connect(config.DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create the domains table if it does not exist."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS domains (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                domain    TEXT NOT NULL,
                source    TEXT NOT NULL,   -- 'dns' or 'sni'
                category  TEXT              -- filled in later stages
            )
            """
        )



