"""
This module creates a SQLite database with four tables (customers, items, orders, and order_list)
and populates the tables with data from a JSON file named 'example_orders.json'.
"""
import sqlite3
import json

conn = sqlite3.connect("db.sqlite")
curr = conn.cursor()

curr.execute(
    """
    CREATE TABLE IF NOT EXISTS customers(
        id INTEGER PRIMARY KEY,
        name CHAR(64) NOT NULL,
        phone CHAR(10) NOT NULL
    );
    """
)

curr.execute(
    """
    CREATE TABLE IF NOT EXISTS items(
        id INTEGER PRIMARY KEY,
        name CHAR(64) NOT NULL,
        price REAL NOT NULL
    );
    """
)

curr.execute(
    """
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY,
        notes TEXT,
        cust_id INTEGER NOT NULL,
        timestamp INTEGER,
        FOREIGN KEY(cust_id) REFERENCES customers(id)
    );
    """
)

curr.execute(
    """
    CREATE TABLE IF NOT EXISTS order_list(
        id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(item_id) REFERENCES items(id)
    );
    """
)

with open('example_orders.json', encoding='utf-8') as file:
    order_list = json.load(file)

orders = {}
customers = {}
items = {}

for order in order_list:
    customers[order['phone']] = order["name"]
    for item in order["items"]:
        items[item["name"]] = item["price"]

for phone, name in customers.items():
    curr.execute("INSERT INTO customers (name, phone) VALUES (?, ?);", (name, phone))

for name, price in items.items():
    curr.execute("INSERT INTO items (name, price) VALUES (?, ?);", (name, price))

for order in order_list:
    curr.execute("SELECT id FROM customers WHERE phone =?;", (order["phone"],))
    cust_id = curr.fetchone()[0]
    curr.execute("INSERT INTO orders (notes, timestamp, cust_id) VALUES (?,?,?);",
    (order["notes"], order["timestamp"], cust_id))
    order_id = curr.lastrowid
    for  item in order["items"]:
        curr.execute("SELECT id FROM items WHERE name=?;" , (item["name"],))
        itm_id = curr.fetchone()[0]
        curr.execute("INSERT INTO order_list (order_id, item_id) VALUES (?,?);",
        (order_id,itm_id))

conn.commit()
conn.close()
