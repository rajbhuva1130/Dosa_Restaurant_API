from fastapi import FastAPI,  HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    
class Customer(BaseModel):
    cust_id: int |  None = None
    name: str
    phone: str

@app.post("/customers/")
def create_cutomer(customer:Customer):
    if  customer.cust_id is not None:
        raise HTTPException(status_code=400, detail="cust_id cannot be set on POST request")
    
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute('INSERT INTO customers (name,phone) VALUES(?,?)', (customer.name, customer.phone))
    customer.cust_id = curr.lastrowid
    conn.commit()
    conn.close()
    return customer
    

@app.get("/customers/{cust_id}")
def read_item(cust_id: int, q=None):
    conn = sqlite3.connect("db.sqlite")
    curr = conn.cursor()
    curr.execute("SELECT id, name, phone FROM customers Where id=?", (cust_id,))
    customer = curr.fetchone()
    conn.close()
    if customer != None:
        return{
            "id" : customer[0],
            "name": customer[1],
            "phone": customer[2]
        }
    
    else:
        raise HTTPException(status_code=404, detail="Customer not found")
        
        