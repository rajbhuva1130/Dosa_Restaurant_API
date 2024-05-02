"""
Module docstring: This module defines a FastAPI application for managing customers,
items, orders, and order lists using a SQLite database.
"""
import sqlite3
from fastapi import FastAPI,  HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    """
    Class docstring: Represents an item with its ID, name, and price.
    """
    item_id: int | None = None
    name: str
    price: float

class Customer(BaseModel):
    """
    Class docstring: Represents a customer with their ID, name, and phone number.
    """
    cust_id: int | None = None
    name: str
    phone: str

class Order(BaseModel):
    """
    Class docstring: Represents an order with its ID, customer ID, notes, and timestamp.
    """
    order_id: int | None = None
    cust_id: int
    notes: str | None = None
    timestamp: int
    order_list: list[int]

class OrderList(BaseModel):
    """
    Class docstring: Represents an order list with its ID, order ID, and item ID.
    """
    order_list_id: int | None = None
    order_id: int
    item_id: int

#Customer Endpoints
@app.post("/customers/")
def create_cutomer(customer:Customer):
    """
    Create a new customer from the provided customer model.
    """
    if  customer.cust_id is not None:
        raise HTTPException(status_code=400,
                            detail="cust_id cannot be set on POST request")

    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute('INSERT INTO customers (name,phone) VALUES(?,?)',
                 (customer.name, customer.phone))
    customer.cust_id = curr.lastrowid
    conn.commit()
    conn.close()
    return customer

@app.get("/customers/{cust_id}")
def read_customer(cust_id: int):
    """
    Retrieve a customer by their customer ID.
    """
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("SELECT id, name, phone FROM customers Where id=?",
                 (cust_id,))
    customer = curr.fetchone()
    conn.close()
    if customer is not None:
        return Customer(cust_id=customer[0], name=customer[1],
                        phone=customer[2])
    raise HTTPException(status_code=404, detail="Customer not found")

@app.put("/customers/{cust_id}")
def update_customer(cust_id:int , customer: Customer):
    """
    update a customer info. by their customer ID.
    """
    if customer.cust_id is not None and customer.cust_id is not cust_id:
        raise HTTPException(status_code=400,
                             detail="Customer ID doesn't match URL")

    customer.cust_id = cust_id
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("UPDATE customers SET name=?,phone=? Where id=?;",
                 (customer.name, customer.phone, cust_id))
    total_changes = conn.total_changes
    conn.commit()
    conn.close()
    if total_changes == 0:
        raise HTTPException(status_code=404,
                             detail="Customer data not found")
    return customer

@app.delete("/customers/{cust_id}")
def delete_customer(cust_id : int):
    """
    Delete a customer by their ID.
    """
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("DELETE from customers WHERE id=?;", (cust_id,))
    total_changes = conn.total_changes
    conn.commit()
    conn.close()
    if total_changes != 1:
        raise HTTPException(status_code=400, detail="id not found")
    return {"deleted": total_changes}

#Items Endpoints
@app.post("/items/")
def create_item(item: Item):
    """
    Create a new item with the specified name and price.
    """
    if  item.item_id is not None:
        raise HTTPException(status_code=400,
                            detail="id cannot be set on POST request")

    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute('INSERT INTO items (name, price) VALUES (?,?)',
                 (item.name, item.price))
    item.item_id = curr.lastrowid
    conn.commit()
    conn.close()
    return item

@app.get("/items/{item_id}")
def read_item(item_id: int):
    """
    Retrieve an item by its ID.
    """
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("SELECT id, name, price FROM items WHERE id=?",
                 (item_id,))
    item = curr.fetchone()
    conn.close()
    if item is not  None:
        return Item(item_id=item[0], name=item[1], price=item[2])
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    """
    Update an item's details based on the item model provided.
    """
    if item.item_id is not None and item.item_id is not item_id:
        raise HTTPException(status_code=400,
                            detail="Item ID does not match URL")

    item.item_id = item_id
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("UPDATE items SET name=?, price=? WHERE id=?",
                 (item.name, item.price, item_id))
    total_changes = conn.total_changes
    conn.commit()
    conn.close()
    if total_changes == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """
    Delete an item by its ID.
    """
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("DELETE FROM items WHERE id=?", (item_id,))
    total_changes = conn.total_changes
    conn.commit()
    conn.close()
    if total_changes != 1:
        raise HTTPException(status_code=404, detail="id not found")
    return {"deleted": total_changes}

#Orders Endpoints
@app.post("/orders/")
def create_order(order: Order):
    """
    Create a new order for a specified customer, including optional notes and a timestamp.
    """
    if  order.order_id is not None:
        raise HTTPException(status_code=400,
                            detail="id cannot be set on POST request")

    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()

    # Check if customer exists
    curr.execute("SELECT id FROM customers WHERE id=?",
                 (order.cust_id,))
    customer = curr.fetchone()
    if customer is None:
        raise HTTPException(status_code=404,
                            detail="Customer not found")

    curr.execute("INSERT INTO orders (cust_id, notes, timestamp) VALUES (?, ?, ?)",
                 (order.cust_id, order.notes, order.timestamp))
    order.order_id = curr.lastrowid

    for item_id in order.order_list:
        curr.execute("SELECT * FROM items WHERE id = ?;", (item_id,))
        if curr.fetchone() is None:
            raise HTTPException(status_code=404,
                                detail=f"Item not found with ID {item_id}")
        curr.execute("INSERT INTO order_list (order_id, item_id) VALUES (?, ?);",
                     (order.order_id, item_id))
    conn.commit()
    conn.close()
    return order

@app.get("/orders/{order_id}")
def read_order(order_id: int):
    """
    Retrieve an order by its ID along with the details of the items in the order.
    """
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()

    # Fetch the order details
    curr.execute("SELECT cust_id, notes, timestamp FROM orders WHERE id=?",
                 (order_id,))
    order_details = curr.fetchone()
    if not order_details:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    order = Order(
        order_id=order_id, cust_id=order_details[0],
        notes=order_details[1], timestamp=order_details[2], order_list=[]
    )

    # Fetch the list of items in the order
    curr.execute("SELECT item_id FROM order_list WHERE order_id=?", (order_id,))
    items = curr.fetchall()
    item_list = []

    # Fetch details for each item
    for item in items:
        curr.execute("SELECT id, name, price FROM items WHERE id=?", (item[0],))
        item_detail = curr.fetchone()
        if item_detail:
            item_list.append(Item(item_id=item_detail[0],
                                  name=item_detail[1], price=item_detail[2]))
    conn.close()

    order.order_list = item_list
    return order

@app.put("/orders/{order_id}")
def update_order(order_id: int, order: Order):
    """
    Update an existing order including its notes, timestamp, and list of items.
    """
    if order.order_id is not None and order.order_id != order_id:
        raise HTTPException(status_code=400,
                            detail="Order ID does not match URL")

    order.order_id = order_id
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()

    # Check if the order exists
    curr.execute("SELECT id FROM orders WHERE id=?", (order_id,))
    if curr.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    curr.execute("UPDATE orders SET notes=?, timestamp=? WHERE id=?",
                 (order.notes, order.timestamp, order_id))

    # Update the list of items in the order
    curr.execute("DELETE FROM order_list WHERE order_id=?", (order_id,))

    for item_id in order.order_list:
        curr.execute("SELECT id FROM items WHERE id=?", (item_id,))
        if curr.fetchone() is None:
            conn.close()
            raise HTTPException(status_code=404,
                                detail=f"Item not found with ID {item_id}")
        curr.execute("INSERT INTO order_list (order_id, item_id) VALUES (?, ?)",
                     (order_id, item_id))
    conn.commit()
    conn.close()

    return order

@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    """
    Delete an existing order and its associated items in the order_list by order ID.
    """
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()

    curr.execute("SELECT id FROM orders WHERE id=?", (order_id,))
    if curr.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")

    curr.execute("DELETE FROM order_list WHERE order_id=?", (order_id,))

    curr.execute("DELETE FROM orders WHERE id=?", (order_id,))
    total_changes = conn.total_changes
    conn.commit()
    conn.close()

    if total_changes == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"deleted": total_changes}
