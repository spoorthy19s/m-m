"""Populate the cafe menu and book catalogue in cafe.db.

Safe to rerun: rows are inserted or updated by their unique catalog keys.
"""

from __future__ import annotations

from database import get_connection, initialize_database


# Keep the catalog definitions here as the backend seed data source.
MENU_ITEMS = [
    ("Hot Beverages", "ESPRESSO", 90, "esp.jpg"),
    ("Hot Beverages", "MASALA TEA", 40, "tea.jpg"),
    ("Hot Beverages", "AMERICANO", 120, "americano.jpg"),
    ("Hot Beverages", "CAPPUCCINO", 150, "cappuccino.jpg"),
    ("Hot Beverages", "MOCHA", 170, "mocha.jpg"),
    ("Hot Beverages", "ICED LATTE", 180, "latte.jpg"),
    ("Hot Beverages", "HOT CHOCOLATE", 160, "hot.jpeg"),
    ("Desserts & Bakes", "BUTTER CROISSANT", 70, "91.jpg"),
    ("Desserts & Bakes", "CHOCOLATE MUFFIN", 80, "92.jpg"),
    ("Desserts & Bakes", "WAFFLE WITH SAUCE", 140, "93.jpg"),
    ("Desserts & Bakes", "BLUEBERRY CHEESECAKE", 160, "96.jpg"),
    ("Desserts & Bakes", "CHOCOLATE SWISS ROLL", 120, "95.jpg"),
    ("Desserts & Bakes", "ICE CREAM SUNDAE", 130, "94.jpg"),
    ("Desserts & Bakes", "FRUIT CAKE (SLICE)", 100, "97.jpg"),
    ("Snacks & Spicy Items", "GRILLED VEG SANDWICH", 90, "81.jpg"),
    ("Snacks & Spicy Items", "VEG PUFF", 50, "82.jpg"),
    ("Snacks & Spicy Items", "SPICY HAKKA NOODLES", 120, "83.jpg"),
    ("Snacks & Spicy Items", "MASALA FRIES", 100, "84.jpg"),
    ("Snacks & Spicy Items", "CHEESE CORN TOAST", 90, "85.jpg"),
    ("Snacks & Spicy Items", "PASTA", 140, "86.jpg"),
    ("Snacks & Spicy Items", "VEG MOMOS", 110, "87.jpg"),
]
