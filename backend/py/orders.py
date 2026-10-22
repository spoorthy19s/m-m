"""Order validation and atomic order creation."""

from __future__ import annotations

import sqlite3
from collections.abc import Sequence


class CustomerNotFound(Exception):
    def __init__(self, customer_id: int) -> None:
        self.customer_id = customer_id
        super().__init__(f"Customer id {customer_id} was not found.")


class MenuItemNotFound(Exception):
    def __init__(self, menu_item_id: int) -> None:
        self.menu_item_id = menu_item_id
        super().__init__(f"Menu item id {menu_item_id} was not found.")


class InvalidOrder(Exception):
    pass


OrderInput = tuple[int, int]  # (menu_item_id, quantity)


def create_order(
    connection: sqlite3.Connection,
    customer_id: int,
    items: Sequence[OrderInput],
) -> dict[str, object]:
    """Create a complete order atomically using prices stored in the database."""
    connection.execute("BEGIN")
    try:
        if not items:
            raise InvalidOrder("Order must contain at least one item.")

        customer = connection.execute(
            "SELECT id FROM customers WHERE id = ?",
            (customer_id,),
        ).fetchone()
        if customer is None:
            raise CustomerNotFound(customer_id)

        priced_items: list[dict[str, int | str]] = []
        seen_item_ids: set[int] = set()
        for menu_item_id, quantity in items:
            if quantity < 1 or quantity > 20:
                raise InvalidOrder(
                    f"Quantity for menu item {menu_item_id} must be between 1 and 20."
                )
            if menu_item_id in seen_item_ids:
                raise InvalidOrder(f"Menu item id {menu_item_id} appears more than once.")
            seen_item_ids.add(menu_item_id)

            menu_item = connection.execute(
                "SELECT id, name, price FROM menu_items WHERE id = ?",
                (menu_item_id,),
            ).fetchone()
            if menu_item is None:
                raise MenuItemNotFound(menu_item_id)

            unit_price = menu_item["price"]
            priced_items.append(
                {
                    "menu_item_id": menu_item["id"],
                    "name": menu_item["name"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "line_total": unit_price * quantity,
                }
            )

        total = sum(int(item["line_total"]) for item in priced_items)
        cursor = connection.execute(
            "INSERT INTO orders (customer_id, total) VALUES (?, ?)",
            (customer_id, total),
        )
        order_id = int(cursor.lastrowid)

        connection.executemany(
            """
            INSERT INTO order_items (order_id, menu_item_id, quantity, unit_price)
            VALUES (?, ?, ?, ?)
            """,
            [
                (order_id, int(item["menu_item_id"]), int(item["quantity"]), int(item["unit_price"]))
                for item in priced_items
            ],
        )
        connection.commit()
        return {"order_id": order_id, "items": priced_items, "total": total}
    except Exception:
        connection.rollback()
        raise

    