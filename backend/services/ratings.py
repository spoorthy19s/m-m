"""Rating validation and database operations."""

from __future__ import annotations

import sqlite3


class RatingCustomerNotFound(Exception):
    def __init__(self, customer_id: int) -> None:
        self.customer_id = customer_id
        super().__init__(f"Customer id {customer_id} was not found.")


class InvalidRating(Exception):
    pass


def save_rating(
    connection: sqlite3.Connection,
    customer_id: int,
    stars: int,
    comment: str | None = None,
) -> str:
    """Validate and insert one rating, returning a short success message."""
    if not 1 <= stars <= 5:
        raise InvalidRating("Stars must be an integer between 1 and 5.")

    cleaned_comment = comment.strip() if comment is not None else None
    if cleaned_comment == "":
        cleaned_comment = None
    if cleaned_comment is not None and len(cleaned_comment) > 500:
        raise InvalidRating("Comment must be 500 characters or fewer.")

    customer = connection.execute(
        "SELECT id FROM customers WHERE id = ?",
        (customer_id,),
    ).fetchone()
    if customer is None:
        raise RatingCustomerNotFound(customer_id)

    # Serialize this check and insert so simultaneous submissions cannot both pass.
    connection.execute("BEGIN IMMEDIATE")
    try:
        customer = connection.execute(
            "SELECT id FROM customers WHERE id = ?",
            (customer_id,),
        ).fetchone()
        if customer is None:
            raise RatingCustomerNotFound(customer_id)

        existing = connection.execute(
            "SELECT 1 FROM ratings WHERE customer_id = ? AND date(created_at) = date('now') LIMIT 1",
            (customer_id,),
        ).fetchone()
        if existing is not None:
            raise InvalidRating("You can submit only one rating per UTC day.")

        connection.execute(
            "INSERT INTO ratings (customer_id, stars, comment) VALUES (?, ?, ?)",
            (customer_id, stars, cleaned_comment),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    return "Rating submitted successfully."
