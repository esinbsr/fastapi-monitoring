
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
import datetime

from app.database import get_db
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services.item_service import ItemService
from app.monitoring.metrics import (
    items_created_total,
    items_read_total,
    items_deleted_total,
    items_total,
    items_price_histogram,
    http_errors_total,
    DatabaseQueryTimer,
)

router = APIRouter(prefix="/items", tags=["items"])

MAX_ITEMS_PER_PAGE = 1000

@router.get("/", response_model=list[ItemResponse])
def get_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupère la liste des items avec pagination."""
    return ItemService.get_all(db, skip, limit)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    with DatabaseQueryTimer():
        item = ItemService.get_by_id(db, item_id)

    if not item:
        http_errors_total.labels(type="not_found").inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )

    items_read_total.inc()
    return item


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: ItemCreate, db: Session = Depends(get_db)):
    try:
        with DatabaseQueryTimer():
            created_item = ItemService.create(db, item_data)

        items_created_total.inc()
        items_total.inc()
        items_price_histogram.observe(item_data.prix)

        return created_item
    except ValueError:
        http_errors_total.labels(type="validation").inc()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid item data",
        )
    except Exception:
        http_errors_total.labels(type="server_error").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_data: ItemUpdate, db: Session = Depends(get_db)):
    item = ItemService.update(db, item_id, item_data)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    with DatabaseQueryTimer():
        deleted = ItemService.delete(db, item_id)

    if not deleted:
        http_errors_total.labels(type="not_found").inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found",
        )

    items_deleted_total.inc()
    items_total.dec()
    return None


def _old_helper_function(data):
    """Cette fonction n'est plus utilisée mais n'a pas été supprimée."""
    return data.upper()
