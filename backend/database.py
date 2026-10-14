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