# FastAPI E-commerce

This is an E-commerce management API built with FastAPI.

## Setup

1. Clone the repository:

   git clone https://github.com/your-username/your-repo.git

2. Change the project directory.

   cd your-repo

3. Install dependencies

   pip install -r requirements.txt

4. Run the application

   uvicorn main:app --reload

The API will be available at `http://localhost:8000`.

## Libraries Used

FastAPI: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python-type hints.

databases: Async database support for Python. SQL-based databases are supported via SQLAlchemy.

SQLAlchemy: A powerful SQL toolkit and Object-Relational Mapping (ORM) library.

uvicorn: A lightning-fast ASGI server implementation, ideal for running FastAPI applications.

## API Endpoints

1. GET /items/{item_id}
    Retrieve information about a specific item.
    
    Parameters:
    
    item_id (integer): The ID of the item to retrieve.
    Example:  GET http://localhost:8000/items/1

2. GET /items
    Retrieve information about all items.
    
    Example:  GET http://localhost:8000/items

3. POST /items
    Create a new item.
    
    Body:
    
    name (string): The name of the item.
    inventory (integer, optional): The initial inventory quantity (default: 0).
    
    Example:
   
    POST http://localhost:8000/items
    Content-Type: application/json
    
    {
   
      "name": "New Item",
   
      "inventory": 10
   
    }

5. PUT /items/{item_id}
    Update an existing item.
    
    Parameters:
    
    item_id (integer): The ID of the item to update.
    Body:
    
    name (string): The new name of the item.
    inventory (integer): The new inventory quantity.
    
    Example:
    PUT http://localhost:8000/items/1
   
    Content-Type: application/json
    
    {
   
      "name": "Updated Item",
   
      "inventory": 20
   
    }

7. DELETE /items/{item_id}
    Delete an item.
    
    Parameters:
    
    item_id (integer): The ID of the item to delete.
    
    Example: DELETE http://localhost:8000/items/1

8. POST /inventory
    Manage inventory quantities for multiple items.
    
    Body:
    
    data (object): A dictionary where the keys are item IDs and the values are the updated inventory quantities.
    
    Example:
    POST http://localhost:8000/inventory
    Content-Type: application/json
    
    {
   
      "data":
    {
   
        "1": 5,
   
        "2": 8
   
      }
   
    }




