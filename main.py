from fastapi import FastAPI,  HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class Item(BaseModel):
    item_id: int |  None = None
    name: str
    # description: str | None = None
    price: float
    # tax: float | None = None
    
class Customer(BaseModel):
    cust_id: int |  None = None
    name: str
    phone: str
    
class Order(BaseModel):
    order_id: int | None = None
    cust_id: int
    notes: str | None = None
    timestamp: int

#Customer Endpoints
@app.post("/customers/")
def create_cutomer(customer:Customer):
    if  customer.cust_id != None:
        raise HTTPException(status_code=400, detail="cust_id cannot be set on POST request")
    
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute('INSERT INTO customers (name,phone) VALUES(?,?)', (customer.name, customer.phone))
    customer.cust_id = curr.lastrowid
    conn.commit()
    conn.close()
    return customer

@app.get("/customers/{cust_id}")
def read_customer(cust_id: int, q=None):
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("SELECT id, name, phone FROM customers Where id=?", (cust_id,))
    customer = curr.fetchone()
    conn.close()
    if customer != None:
        return Customer(cust_id = customer[0], name= customer[1],  phone=customer[2])
    else:
        raise HTTPException(status_code=404, detail="Customer not found")

@app.put("/customers/{cust_id}")
def update_customer(cust_id:int , customer: Customer):
    if customer.cust_id != None and customer.cust_id != cust_id:
        raise  HTTPException(status_code=400, detail="Customer ID doesn't match URL")
    
    customer.cust_id = cust_id
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("UPDATE customers SET name=?,phone=? Where id=?;", (customer.name, customer.phone, cust_id))
    total_changes = conn.total_changes
    conn.commit()
    conn.close()
    if total_changes == 0:
        raise   HTTPException(status_code=404,detail="Customer data not found")
    return customer

@app.delete("/customers/{cust_id}")
def delete_customer(cust_id : int):
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
    if  item.item_id != None:
        raise HTTPException(status_code=400, detail="id cannot be set on POST request")
    
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute('INSERT INTO items (name, price) VALUES (?,?)', 
                 (item.name, item.price))
    item.item_id = curr.lastrowid
    conn.commit()
    conn.close()
    return item

@app.get("/items/{item_id}")
def read_item(item_id: int, q=None):
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("SELECT id, name, price FROM items WHERE id=?", (item_id,))
    item = curr.fetchone()
    conn.close()
    if item !=  None:
        return Item(item_id = item[0], name = item[1], price = item[2])
    else:
        raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item.item_id != None and item.item_id != item_id:
        raise HTTPException(status_code=400, detail="Item ID does not match URL")

    item.item_id = item_id
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("UPDATE items SET name=?, price=? WHERE id=?", 
                 (item.name, item.price, item_id))
    total_changes = conn.total_changes
    conn.commit()
    conn.close()
    if total_changes == 0:
        raise   HTTPException(status_code=404, detail="Item not found")
    return item
    
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
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
    if  order.order_id != None:
        raise HTTPException(status_code=400, detail="id cannot be set on POST request")
    
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    
    # Check if customer exists
    curr.execute("SELECT id FROM customers WHERE id=?", (order.cust_id,))
    customer = curr.fetchone()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    curr.execute("INSERT INTO orders (cust_id, notes, timestamp) VALUES (?, ?, ?)", 
                 (order.cust_id, order.notes, order.timestamp))
    order.order_id = curr.lastrowid
    conn.commit()
    conn.close()
    return order

@app.get("/orders/{order_id}")
def read_order(order_id: int):
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("SELECT id, cust_id, notes, timestamp FROM orders WHERE id=?", (order_id,))
    order_data = curr.fetchone()
    conn.close()
    if order_data != None:
        order = Order(order_id=order_data[0], cust_id=order_data[1], notes=order_data[2], timestamp=order_data[3])
        return order
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@app.put("/orders/{order_id}")
def update_order(order_id: int, order: Order):
    if order.order_id != None and order.order_id != order_id:
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
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("DELETE FROM orders WHERE id=?", (order_id,))
    total_changes = conn.total_changes
    conn.commit()
    conn.close()
    if total_changes != 1:
        raise HTTPException(status_code=404, detail="id not found")
    return {"deleted": total_changes}