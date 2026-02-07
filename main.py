from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "postgresql://admin:admin123@localhost:5432/mydb"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI(title="FastAPI CRUD")

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ORM MODEL
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

# Create tables (for learning/dev only)
Base.metadata.create_all(bind=engine)

# SCHEMAS
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ItemResponse(ItemCreate):
    id: int

    class Config:
        orm_mode = True  # IMPORTANT

# CREATE
@app.post("/items", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    try:
        db_item = Item(name=item.name, description=item.description)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, "Database error")

# READ ALL
@app.get("/items", response_model=List[ItemResponse])
def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()

# READ ONE
@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()

    if not item:
        raise HTTPException(404, "Item not found")

    return item

# UPDATE
@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()

    if not db_item:
        raise HTTPException(404, "Item not found")

    db_item.name = item.name
    db_item.description = item.description

    try:
        db.commit()
        db.refresh(db_item)
        return db_item
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, "Database error")

# DELETE
@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()

    if not db_item:
        raise HTTPException(404, "Item not found")

    try:
        db.delete(db_item)
        db.commit()
        return {"message": "Item deleted"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(500, "Database error")