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

BOOKS = [
    ("A SHIMLA AFFAIR", "General Fiction", "11.jpg"),
    ("MARROW", "General Fiction", "16.jpg"),
    ("BUTCHER & BLACKBIRD", "General Fiction", "17.jpeg"),
    ("KING OF ENVY", "General Fiction", "13.jpg"),
    ("GOD OF WAR", "General Fiction", "15.jpg"),
    ("DAYS AT THE TORUNKA CAFE", "General Fiction", "12.jpg"),
    ("SHATTER ME", "General Fiction", "14.jpg"),
    ("THE METAMORPHOSIS", "Literary Fiction", "31.jpg"),
    ("PRIDE AND PREJUDICE", "Classic Romance", "36.jpg"),
    ("ANIMAL FARM", "Political Satire", "32.jpg"),
    ("WHITE NIGHTS", "Romance", "37.jpg"),
    ("NORWEGIAN WOOD", "Literary Fiction", "33.jpg"),
    ("CRIME AND PUNISHMENT", "Psychological Fiction", "35.jpg"),
    ("THE BELL JAR", "Literary Fiction", "34.jpg"),
    ("HOW TO KILL MEN AND GET AWAY WITH IT", "Thrillers", "21.jpeg"),
    ("SHARP OBJECTS", "Thrillers", "22.jpg"),
    ("NONE OF THIS IS TRUE", "Thrillers", "23.jpg"),
    ("THE FAVOURITE GIRL", "Thrillers", "27.jpg"),
    ("THE FAMILY UPSTAIRS", "Thrillers", "25.jpg"),
    ("ROCK PAPER SCISSORS", "Thrillers", "26.jpg"),
    ("NEVER LIE", "Thrillers", "24.jpg"),
]

def seed_database() -> tuple[int, int]:
    """Create tables and idempotently insert/update the catalog rows."""
    initialize_database()
    connection = get_connection()
    try:
        connection.executemany(
            """
            INSERT INTO menu_items (category, name, price, image)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(category, name) DO UPDATE SET
                price = excluded.price,
                image = excluded.image
            """,
            MENU_ITEMS,
        )
        connection.executemany(
            """
            INSERT INTO books (title, genre, image)
            VALUES (?, ?, ?)
            ON CONFLICT(title, genre) DO UPDATE SET
                image = excluded.image
            """,
            BOOKS,
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return len(MENU_ITEMS), len(BOOKS)


if __name__ == "__main__":
    menu_count, book_count = seed_database()
    print(f"Seeded {menu_count} menu items and {book_count} books.")
outputs/m-m/README.md
