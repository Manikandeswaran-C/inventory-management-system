"""
Items router — all /items endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import (
    ItemCreate,
    ItemListResponse,
    ItemResponse,
    MessageResponse,
    StockUpdate,
)

router = APIRouter()


@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new inventory item",
    responses={
        201: {"description": "Item created successfully"},
        422: {"description": "Validation error — e.g. negative quantity or blank name"},
    },
)
def add_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
) -> ItemResponse:
    """
    **Add a new item** to the inventory.

    - `name` must be a non-empty string.
    - `quantity` must be **≥ 0** (negative stock is forbidden).
    - A `low_stock` flag is automatically set when quantity ≤ 10.
    """
    created = crud.create_item(db=db, item_data=item)
    return created


@router.get(
    "/",
    response_model=ItemListResponse,
    summary="List all inventory items",
    responses={
        200: {"description": "Paginated list of all items"},
    },
)
def list_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    db: Session = Depends(get_db),
) -> ItemListResponse:
    """
    **Retrieve all items** in the inventory.

    Supports pagination via `skip` and `limit` query parameters.
    Also returns summary counts: total items and how many are low-stock.
    """
    items = crud.get_all_items(db=db, skip=skip, limit=limit)
    total = crud.count_items(db=db)
    low_stock_count = crud.count_low_stock_items(db=db)

    return ItemListResponse(
        items=items,
        total=total,
        low_stock_count=low_stock_count,
    )


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    summary="Get a single inventory item",
    responses={
        200: {"description": "Item found"},
        404: {"description": "Item not found"},
    },
)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
) -> ItemResponse:
    """
    **Retrieve a single item** by its ID.

    Returns 404 if no item exists with the given `item_id`.
    """
    item = crud.get_item(db=db, item_id=item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id={item_id} was not found.",
        )
    return item


@router.patch(
    "/{item_id}/stock",
    response_model=ItemResponse,
    summary="Update stock quantity for an item",
    responses={
        200: {"description": "Stock updated successfully"},
        400: {"description": "Business rule violation (e.g. negative stock)"},
        404: {"description": "Item not found"},
        422: {"description": "Validation error"},
    },
)
def update_stock(
    item_id: int,
    stock_update: StockUpdate,
    db: Session = Depends(get_db),
) -> ItemResponse:
    """
    **Update the stock quantity** of an existing item.

    ### ⚠️ Trick Logic (Business Rules)
    | Rule | Detail |
    |------|--------|
    | No negative stock | `quantity < 0` → **400 Bad Request** |
    | Low-stock alert   | `quantity ≤ 10` → `low_stock` flag set to `true` |

    The `low_stock` field in the response reflects the current alert state.
    """
    # Extra safety net beyond Pydantic validation
    if stock_update.quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock cannot be negative. Quantity must be >= 0.",
        )

    updated_item = crud.update_item_stock(
        db=db, item_id=item_id, new_quantity=stock_update.quantity
    )

    if updated_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id={item_id} was not found.",
        )

    return updated_item


@router.delete(
    "/{item_id}",
    response_model=MessageResponse,
    summary="Delete an inventory item",
    responses={
        200: {"description": "Item deleted"},
        404: {"description": "Item not found"},
    },
)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """
    **Delete an item** from the inventory by ID.
    """
    item = crud.get_item(db=db, item_id=item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id={item_id} was not found.",
        )
    db_item = crud.get_item(db=db, item_id=item_id)
    db.delete(db_item)
    db.commit()
    return MessageResponse(
        message="Item deleted successfully.",
        detail=f"Item '{item.name}' (id={item_id}) has been removed from inventory.",
    )
