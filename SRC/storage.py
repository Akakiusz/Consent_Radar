"""Stage 2: SQLite persistence — read/write captured domains."""

# Import standard libraries
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

import config

# Context manager for SQLite connection, ensuring commit and close.
@contextmanager
def _connect():
    conn = sqlite3.connect(config.DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

# Create the domains table if it does not exist.
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
# Define a function to insert a domain into the database with its source and optional category.
def insert_domain(domain: str, source: str, category: str | None = None):
    """Insert one observed domain."""
    ts = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO domains (timestamp, domain, source, category) "
            "VALUES (?, ?, ?, ?)",
            (ts, domain, source, category),
        )
# Fetch all rows from the domains table, ordered by id (oldest first).
def fetch_all():
    """Return all rows as a list of tuples."""
    with _connect() as conn:
        return conn.execute(
            "SELECT timestamp, domain, source, category FROM domains "
            "ORDER BY id"
        ).fetchall()