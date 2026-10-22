from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterator


BACKEND_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BACKEND_DIR / "schema.sql"
DB_PATH = Path(os.environ.get("CAFE_DB_PATH", BACKEND_DIR / "cafe.db"))

def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection with row access and foreign keys enabled."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    # SQLite disables foreign-key enforcement by default, per connection.
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize_database() -> None:
    """Create the database tables from schema.sql if they do not exist."""
    if not SCHEMA_PATH.is_file():
        raise FileNotFoundError(f"Database schema was not found: {SCHEMA_PATH}")

    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    connection = get_connection()
    try:
        connection.executescript(schema)
        connection.commit()
    finally:
        connection.close()


def get_db() -> Iterator[sqlite3.Connection]:
    """Yield one connection for a request and close it when the request ends.

    Use as a generator dependency in a web framework, or call ``next()`` and
    close the generator in a ``finally`` block in a framework-free handler.
    """
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()