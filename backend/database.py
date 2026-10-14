from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterator


BACKEND_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BACKEND_DIR / "schema.sql"
DB_PATH = Path(os.environ.get("CAFE_DB_PATH", BACKEND_DIR / "cafe.db"))
