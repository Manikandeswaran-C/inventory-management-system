-- seed_data.sql
-- Populate the inventory with sample data for initial testing.
-- Run after Alembic migrations:  sqlite3 inventory.db < seed_data.sql

INSERT INTO items (name, quantity, low_stock) VALUES
    ('Wireless Mouse',         120, 0),
    ('Mechanical Keyboard',     45, 0),
    ('USB-C Hub',               8,  1),   -- low stock
    ('27" Monitor',             30, 0),
    ('Laptop Stand',            5,  1),   -- low stock
    ('Webcam HD 1080p',         22, 0),
    ('HDMI Cable 2m',          200, 0),
    ('Ethernet Cable 5m',       15, 0),
    ('Power Strip 6-outlet',    3,  1),   -- low stock
    ('AA Batteries (pack 4)',  500, 0),
    ('Desk Lamp LED',           10, 1),   -- low stock (exactly at threshold)
    ('Office Chair Cushion',    0,  1),   -- out of stock → low stock
    ('Noise-Cancelling Headset',18, 0),
    ('Mousepad XL',             60, 0),
    ('Portable SSD 1TB',        7,  1);   -- low stock
