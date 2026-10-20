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
    