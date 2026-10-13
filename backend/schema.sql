-- Margins & Mugs SQLite schema
-- Run PRAGMA foreign_keys = ON for every database connection.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL CHECK (length(trim(name)) > 0),
    phone       TEXT NOT NULL UNIQUE CHECK (length(trim(phone)) > 0),
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS menu_items (
    id          INTEGER PRIMARY KEY,
    category    TEXT NOT NULL CHECK (length(trim(category)) > 0),
    name        TEXT NOT NULL CHECK (length(trim(name)) > 0),
    price       INTEGER NOT NULL CHECK (price >= 0),
    image       TEXT,
    UNIQUE (category, name)
);

CREATE TABLE IF NOT EXISTS books (
    id          INTEGER PRIMARY KEY,
    title       TEXT NOT NULL CHECK (length(trim(title)) > 0),
    genre       TEXT NOT NULL CHECK (length(trim(genre)) > 0),
    image       TEXT,
    UNIQUE (title, genre)
);

CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    total       INTEGER NOT NULL CHECK (total >= 0),
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS order_items (
    id           INTEGER PRIMARY KEY,
    order_id     INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    quantity     INTEGER NOT NULL CHECK (quantity > 0),
    -- Snapshot the menu price at purchase time; do not recalculate old orders
    -- from menu_items.price.
    unit_price   INTEGER NOT NULL CHECK (unit_price >= 0),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE RESTRICT,
    UNIQUE (order_id, menu_item_id)
);

CREATE TABLE IF NOT EXISTS ratings (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    stars       INTEGER NOT NULL CHECK (stars BETWEEN 1 AND 5),
    comment     TEXT,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_orders_customer_created
    ON orders(customer_id, created_at);

CREATE INDEX IF NOT EXISTS idx_order_items_order
    ON order_items(order_id);

CREATE INDEX IF NOT EXISTS idx_ratings_customer_created
    ON ratings(customer_id, created_at);

-- `books.genre` is a free-form tag, not the old broad category label.
-- Examples: use `Classic Romance` for Pride and Prejudice and `Political Satire`
-- for Animal Farm instead of labeling either title as `Non-Fiction`.