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






