from fastapi import FastAPI, HTTPException
from typing import Dict, List
from pydantic import BaseModel
from databases import Database
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create the FastAPI instance
app = FastAPI()

# Define the database connection URL
DATABASE_URL = "sqlite:///./database.db"

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create the database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Create the database models
Base = declarative_base()


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    quantity = Column(Integer)

    item = relationship("Item", backref="inventory")


Base.metadata.create_all(bind=engine)


# Define the Pydantic models
class ItemCreate(BaseModel):
    name: str
    inventory: int = 0


class ItemUpdate(BaseModel):
    id: int
    name: str
    inventory: int


class InventoryUpdate(BaseModel):
    data: Dict[int, int]


# Update the ItemResponse model
class ItemResponse(BaseModel):
    id: int
    name: str
    stock: str = "In Stock"


# Update the read_item endpoint
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    inventory = db.query(Inventory).filter(Inventory.item_id == item.id).first()
    stock = "Out of Stock" if inventory and inventory.quantity <= 0 else "In Stock"
    item_response = ItemResponse(id=item.id, name=item.name, stock=stock)
    return item_response


# Update the get_all_items endpoint
@app.get("/items")
async def get_all_items():
    items = db.query(Item).all()
    item_responses = []
    for item in items:
        inventory = db.query(Inventory).filter(Inventory.item_id == item.id).first()
        stock = "Out of Stock" if inventory and inventory.quantity <= 0 else "In Stock"
        item_response = ItemResponse(id=item.id, name=item.name, stock=stock)
        item_responses.append(item_response)
    return item_responses



@app.post("/items")
async def create_item(item: ItemCreate):
    db_item = Item(name=item.name)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    initial_quantity = item.inventory
    stock = "In Stock" if initial_quantity > 0 else "Out of Stock"

    # Create the inventory for the item
    inventory = Inventory(item_id=db_item.id, quantity=initial_quantity)
    db.add(inventory)
    db.commit()
    db.refresh(inventory)

    item_response = ItemResponse(
        id=db_item.id,
        name=db_item.name,
        stock=stock
    )
    return {"message": "Item created", "item": item_response}


# Update the update_item endpoint
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: ItemUpdate):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.name = item.name

    # Get the inventory for the item
    inventory = db.query(Inventory).filter(Inventory.item_id == item_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    previous_quantity = inventory.quantity
    inventory.quantity = item.inventory

    # Update the stock field based on the updated inventory quantity
    if inventory.quantity > 0:
        inventory.item.stock = "In Stock"
    else:
        inventory.item.stock = "Out of Stock"

    db.commit()
    db.refresh(db_item)
    db.refresh(inventory)

    # Check if the stock status has changed and update read_item and get_all_items accordingly
    if previous_quantity <= 0 and inventory.quantity > 0:
        items = db.query(Item).all()
        for item in items:
            inventory = db.query(Inventory).filter(Inventory.item_id == item.id).first()
            stock = "Out of Stock" if inventory and inventory.quantity <= 0 else "In Stock"
            item.stock = stock

    item_response = ItemUpdate(
        id=db_item.id,
        name=db_item.name,
        inventory=inventory.quantity,
    )
    return {"message": "Item updated", "item": item_response}


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}


# API for managing inventory
@app.post("/inventory")
async def manage_inventory(inventory_update: InventoryUpdate):
    for item_id, quantity in inventory_update.data.items():
        db_inventory = db.query(Inventory).filter(Inventory.item_id == item_id).first()
        if not db_inventory:
            db_item = db.query(Item).filter(Item.id == item_id).first()
            if not db_item:
                raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
            db_inventory = Inventory(item_id=item_id, quantity=quantity)
            db.add(db_inventory)
        else:
            # Subtract the quantity from the existing inventory
            db_inventory.quantity -= quantity
            
            # Update the stock field based on the updated inventory quantity
            if db_inventory.quantity > 0:
                db_inventory.item.stock = "In Stock"
            else:
                db_inventory.item.stock = "Out of Stock"
                
            if db_inventory.quantity < 0:
                raise HTTPException(status_code=400, detail=f"Item with ID {item_id} is out of stock")
                
        db.commit()
        db.refresh(db_inventory)
    return {"message": "Inventory updated"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
