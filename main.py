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
    # description: str | None = None
    price: float
    # tax: float | None = None

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
    conn.commit()
    conn.close()
    return order

@app.get("/orders/{order_id}")
def read_order(order_id: int):
    """
    Retrieve an order by its ID, including customer details and timestamp.
    """
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("SELECT id, cust_id, notes, timestamp FROM orders WHERE id=?",
                 (order_id,))
    order_data = curr.fetchone()
    conn.close()
    if order_data is not None:
        order = Order(order_id=order_data[0], cust_id=order_data[1],
                      notes=order_data[2], timestamp=order_data[3])
        return order
    raise HTTPException(status_code=404, detail="Order not found")

@app.put("/orders/{order_id}")
def update_order(order_id: int, order: Order):
    """
    Update an existing order's details including customer ID, notes, and timestamp.
    """
    if order.order_id is not None and order.order_id is not order_id:
        raise HTTPException(status_code=400, detail="Order ID doesn't match URL")

    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()

    # Check if customer exists
    curr.execute("SELECT id FROM customers WHERE id=?", (order.cust_id,))
    customer = curr.fetchone()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    order.order_id = order_id
    curr.execute("UPDATE orders SET cust_id=?, notes=?, timestamp=? WHERE id=?",
                 (order.cust_id, order.notes, order.timestamp, order_id))
    total_changes = conn.total_changes
    conn.commit()
    conn.close()
    if total_changes == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    """
    Delete an order by its ID.
    """
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("DELETE FROM orders WHERE id=?", (order_id,))
    total_changes = conn.total_changes
    conn.commit()
    conn.close()
    if total_changes != 1:
        raise HTTPException(status_code=404, detail="id not found")
    return {"deleted": total_changes}

# Order List Endpoints
@app.post("/order_list/")
def create_order_list(order_list: OrderList):
    """
    Create a new order list entry linking an order with an item.
    """
    if  order_list.order_list_id is not None:
        raise HTTPException(status_code=400, detail="id cannot be set on POST request")

    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()

    # Check if order exists
    curr.execute("SELECT id FROM orders WHERE id=?", (order_list.order_id,))
    order = curr.fetchone()
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")

    # Check if item exists
    curr.execute("SELECT id FROM items WHERE id=?", (order_list.item_id,))
    item = curr.fetchone()
    if item is None:
        raise HTTPException(status_code=404, detail="item not found")

    curr.execute("INSERT INTO order_list (order_id, item_id) VALUES (?, ?)",
                 (order_list.order_id, order_list.item_id))
    order_list.order_list_id = curr.lastrowid
    conn.commit()
    conn.close()
    return order_list

@app.get("/order_list/{order_list_id}")
def read_order_list(order_list_id: int):
    """
    Retrieve an order list entry by its ID, showing linked order and item IDs.
    """
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("SELECT id, order_id, item_id FROM order_list WHERE id=?",
                 (order_list_id,))
    order_list_data = curr.fetchone()
    conn.close()
    if order_list_data is not None:
        order_list = OrderList(order_list_id=order_list_data[0],
                                order_id=order_list_data[1], item_id=order_list_data[2])
        return order_list
    raise HTTPException(status_code=404, detail="id not found")

@app.put("/order_list/{order_list_id}")
def update_order_list(order_list_id: int, order_list: OrderList):
    """
    Update an existing order list entry, linking new or updated order and item IDs.
    """
    if order_list.order_list_id is not None and order_list.order_list_id is not order_list_id:
        raise HTTPException(status_code=400, detail="Order_List ID doesn't match URL")

    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()

    # Check if order exists
    curr.execute("SELECT id FROM orders WHERE id=?", (order_list.order_id,))
    order = curr.fetchone()
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")

    # Check if item exists
    curr.execute("SELECT id FROM items WHERE id=?", (order_list.item_id,))
    item = curr.fetchone()
    if item is None:
        raise HTTPException(status_code=404, detail="item not found")

    order_list.order_list_id = order_list_id
    curr.execute("UPDATE order_list SET order_id=?, item_id=? WHERE id=?",
                 (order_list.order_id, order_list.item_id, order_list_id))
    total_changes = conn.total_changes
    conn.commit()
    conn.close()
    if total_changes == 0:
        raise HTTPException(status_code=404, detail="Order_list id not found")
    return order_list

@app.delete("/order_list/{order_list_id}")
def delete_order_list(order_list_id: int):
    """
    Delete an order list entry by its ID.
    """
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("DELETE from order_list where id=?", (order_list_id,))
    total_changes = conn.total_changes
    conn.commit()
    conn.close()
    if total_changes != 1:
        raise HTTPException(status_code=404, detail="id not found")
    return {"deleted": total_changes}
