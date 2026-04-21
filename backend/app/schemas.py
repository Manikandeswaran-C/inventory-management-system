"""
Pydantic schemas for request validation and response serialization.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# ── Request schemas ────────────────────────────────────────────────────────────

class ItemCreate(BaseModel):
    """Schema for creating a new inventory item."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the inventory item",
        examples=["Widget A"],
    )
    quantity: int = Field(
        ...,
        ge=0,
        description="Initial stock quantity (must be >= 0)",
        examples=[50],
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Item name must not be blank or whitespace only.")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {"name": "Widget A", "quantity": 50}
        }
    }


class StockUpdate(BaseModel):
    """Schema for updating the stock quantity of an existing item."""
    quantity: int = Field(
        ...,
        description=(
            "New absolute stock quantity. "
            "Must be >= 0 — negative stock is not allowed."
        ),
        examples=[25],
    )

    @field_validator("quantity")
    @classmethod
    def quantity_must_not_be_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError(
                "Stock cannot be negative. "
                "Quantity must be greater than or equal to 0."
            )
        return v

    model_config = {
        "json_schema_extra": {
            "example": {"quantity": 25}
        }
    }


# ── Response schemas ───────────────────────────────────────────────────────────

class ItemResponse(BaseModel):
    """Schema for returning a single inventory item."""
    id: int = Field(..., description="Unique item identifier")
    name: str = Field(..., description="Name of the inventory item")
    quantity: int = Field(..., description="Current stock quantity")
    low_stock: bool = Field(
        ...,
        description="True when quantity is at or below the low-stock threshold (10 units)",
    )
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class ItemListResponse(BaseModel):
    """Schema for a paginated list of inventory items."""
    items: list[ItemResponse]
    total: int = Field(..., description="Total number of items in inventory")
    low_stock_count: int = Field(..., description="Number of items with low stock")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    detail: Optional[str] = None
