Dosa Restaurant REST API
------------------------

This project is a REST API backend for a Dosa restaurant, built using FastAPI and SQLite database. The API provides CRUD (Create, Read, Update, Delete) operations for four entities: customers, items, orders, and order_list.


Requirements
------------
Python 3.x

FastAPI

SQLite

Installation
------------

Clone the repository:

https://github.com/rajbhuva1130/Dosa_Restaurant_API.git

Navigate to the project directory:

cd dosa-restaurant-api

Install the required dependencies:

pip install -r requirements.txt

Database Setup

python init_db.py

Start the FastAPI server by running main.py:

uvicorn main:app --reload

The API will be available at http://127.0.0.1:8000.

For API in docs Formate at http://127.0.0.1:8000/docs.

API Endpoints
-------------

Customers
---------
POST /customers: Create a new customer

GET /customers/{id}: Retrieve a customer by ID

DELETE /customers/{id}: Delete a customer by ID

PUT /customers/{id}: Update a customer by ID

Items
-----
POST /items: Create a new item

GET /items/{id}: Retrieve an item by ID

DELETE /items/{id}: Delete an item by ID

PUT /items/{id}: Update an item by ID

Orders
------
POST /orders: Create a new order

GET /orders/{id}: Retrieve an order by ID

DELETE /orders/{id}: Delete an order by ID

PUT /orders/{id}: Update an order by ID

Order list
---------
POST /order_list: Create a new order list

GET /order_list/{id}: Retrieve an order list by ID

DELETE /order_list/{id}: Delete an order list by ID

PUT /order_list/{id}: Update an order list by ID
