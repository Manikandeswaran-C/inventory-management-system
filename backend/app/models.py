"""
SQLAlchemy ORM models for Inventory Management.
"""
from sqlalchemy import Column, Integer, Text, Boolean, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Item(Base):
    """
    Inventory item model.

    Attributes:
        id       : Primary key.
        name     : Name/description of the item.
        quantity : Current stock quantity (must be >= 0).
        low_stock: True when quantity <= LOW_STOCK_THRESHOLD.
        created_at: Timestamp of creation.
        updated_at: Timestamp of last stock update.
    """

    __tablename__ = "items"

    LOW_STOCK_THRESHOLD = 10  # Alert threshold

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(Text, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    low_stock = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def update_low_stock_flag(self) -> None:
        """Recalculate and persist the low_stock alert flag."""
        self.low_stock = self.quantity <= self.LOW_STOCK_THRESHOLD

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Item id={self.id} name='{self.name}' "
            f"quantity={self.quantity} low_stock={self.low_stock}>"
        )
