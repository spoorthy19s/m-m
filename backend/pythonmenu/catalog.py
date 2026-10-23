"""Read-only catalog queries and grouping helpers."""

from __future__ import annotations

import sqlite3


def menu_grouped_by_category(connection: sqlite3.Connection) -> dict[str, list[dict[str, object]]]:
    """Return menu rows grouped by category, preserving their seeded order."""
    rows = connection.execute(
        """
        SELECT id, category, name, price, image
        FROM menu_items
        ORDER BY id
        """
    ).fetchall()

    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(row["category"], []).append(
            {
                "id": row["id"],
                "name": row["name"],
                "price": row["price"],
                "image": row["image"],
            }
        )
    return grouped


def books_grouped_by_genre(connection: sqlite3.Connection) -> dict[str, list[dict[str, object]]]:
    """Return book rows grouped by genre, preserving their seeded order."""
    rows = connection.execute(
        """
        SELECT id, title, genre, image
        FROM books
        ORDER BY id
        """
    ).fetchall()

    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(row["genre"], []).append(
            {
                "id": row["id"],
                "title": row["title"],
                "genre": row["genre"],
                "image": row["image"],
            }
        )
    return grouped
