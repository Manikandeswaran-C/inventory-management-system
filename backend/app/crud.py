"""
CRUD operations layer — separates database logic from route handlers.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import Item
from app.schemas import ItemCreate


def get_item(db: Session, item_id: int) -> Optional[Item]:
    """Fetch a single item by primary key."""
    return db.query(Item).filter(Item.id == item_id).first()


def get_all_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Item]:
    """Fetch all items with optional pagination."""
    return db.query(Item).offset(skip).limit(limit).all()


def count_items(db: Session) -> int:
    """Return total number of items in the inventory."""
    return db.query(Item).count()


def count_low_stock_items(db: Session) -> int:
    """Return how many items currently have low stock."""
    return db.query(Item).filter(Item.low_stock == True).count()  # noqa: E712


def create_item(db: Session, item_data: ItemCreate) -> Item:
    """
    Persist a new item to the database.

    The low_stock flag is computed immediately on creation.
    """
    db_item = Item(
        name=item_data.name,
        quantity=item_data.quantity,
    )
    db_item.update_low_stock_flag()
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    except SQLAlchemyError as exc:
        db.rollback()
        raise exc
    return db_item


def update_item_stock(db: Session, item_id: int, new_quantity: int) -> Optional[Item]:
    """
    Update stock quantity for an existing item.

    ⚠️  TRICK LOGIC:
        - new_quantity < 0  → rejected at schema layer (Pydantic validator).
        - Caller must already have validated the value is >= 0.
        - After update, low_stock flag is recalculated automatically.

    Returns None if the item does not exist.
    """
    db_item = get_item(db, item_id)
    if db_item is None:
        return None

    db_item.quantity = new_quantity
    db_item.update_low_stock_flag()

    try:
        db.commit()
        db.refresh(db_item)
    except SQLAlchemyError as exc:
        db.rollback()
        raise exc

    return db_item
