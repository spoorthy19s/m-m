"""Customer login validation and database operations."""

from __future__ import annotations

import re
import sqlite3


def normalize_login(name: str, phone: str) -> tuple[str, str]:
    """Trim a name and normalize a phone using the frontend's rules."""
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Name must not be empty.")

    cleaned_phone = re.sub(r"[\s()+-]", "", phone)
    if not re.fullmatch(r"\d{7,15}", cleaned_phone):
        raise ValueError(
            "Phone must contain 7 to 15 digits after spaces, brackets, plus signs, and dashes are removed."
        )

    return cleaned_name, cleaned_phone


def upsert_customer(
    connection: sqlite3.Connection,
    name: str,
    phone: str,
) -> dict[str, int | str]:
    """Insert a customer or update their name when the phone already exists."""
    connection.execute(
        """
        INSERT INTO customers (name, phone)
        VALUES (?, ?)
        ON CONFLICT(phone) DO UPDATE SET name = excluded.name
        """,
        (name, phone),
    )
    connection.commit()

    row = connection.execute(
        "SELECT id, name FROM customers WHERE phone = ?",
        (phone,),
    ).fetchone()
    if row is None:
        raise RuntimeError("Customer upsert succeeded but the row could not be found.")
    return {"customer_id": row["id"], "name": row["name"]}
