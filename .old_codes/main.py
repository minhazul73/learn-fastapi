from fastapi import Depends, FastAPI
from models import Item
from database import session, engine
import database_models
from sqlalchemy.orm import Session

app = FastAPI()

database_models.Base.metadata.create_all(bind=engine)

items = [
    Item(id=1, name="Item 1", description="This is item 1", price=10.0, tax=0.5),
    Item(id=2, name="Item 2", description="This is item 2", price=20.0, tax=1.0),
    Item(id=3, name="Item 3", description="This is item 3", price=30.0, tax=1.5),
]

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    db = session()
    count = db.query(database_models.Item).count()
    if count > 0:
        db.close()
        return
    
    for item in items:
        db.add(database_models.Item(**item.model_dump()))
        
    db.commit()
    db.close()
    

init_db()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/")
async def read_items(db: Session = Depends(get_db)):
    db_items = db.query(database_models.Item).all()
    return db_items

@app.get("/get-items/{item_id}")
async def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(database_models.Item).filter(database_models.Item.id == item_id).first()
    if item:
        return item
    return {"error": "Item not found"}

@app.post("/create-item")
async def create_item(item: Item, db: Session = Depends(get_db)):
    items.append(item)
    db.add(database_models.Item(**item.model_dump()))
    db.commit()
    return item

@app.put("/update-item/{item_id}")
async def update_item(item_id: int, item: Item, db: Session = Depends(get_db)):
    db_item = db.query(database_models.Item).filter(database_models.Item.id == item_id).first()
    if db_item:
        for key, value in item.model_dump().items():
            setattr(db_item, key, value)
        db.commit()
        return db_item
    return {"error": "Item not found"}

@app.delete("/delete-item/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(database_models.Item).filter(database_models.Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return {"message": "Item deleted successfully"}
    return {"error": "Item not found"}