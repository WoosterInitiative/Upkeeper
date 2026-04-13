# pyright: reportCallInDefaultInitializer=false
# ruff: noqa: B008
"""Created by upkeeper.devtools.create_module."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from upkeeper.core import JSONDict, slugify
from upkeeper.database import get_db
from upkeeper.logging_config import get_logger
from upkeeper.models.base import generate_unique_slug
from upkeeper.models.main import TrackedItem
from upkeeper.routers.base import BaseDetailResponse, TimestampResponseMixin

logger = get_logger(__name__)


router = APIRouter(prefix="/items", tags=["items"])


class TrackedItemResponse(TimestampResponseMixin):
    id: int
    name: str
    slug: str
    location: str | None = None
    notes: str | None = None
    attributes: JSONDict


@router.get("", response_model=list[TrackedItemResponse])
def list_tracked_items(session: Session = Depends(get_db)) -> list[TrackedItem]:
    """Endpoint to list all tracked items."""
    return session.query(TrackedItem).all()


class TrackedItemCreateRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    location: Annotated[str | None, Field(max_length=100)] = None
    notes: Annotated[str | None, Field(max_length=255)] = None
    attributes: JSONDict
    slug: Annotated[str | None, Field(max_length=100)] = None

    @property
    def get_slug(self) -> str:
        """Get the slug value, ensuring it is generated if not explicitly set."""
        return self.slug or slugify(self.name)


@router.post("", response_model=TrackedItemResponse)
def create_tracked_item(
    item: TrackedItemCreateRequest, session: Session = Depends(get_db)
) -> TrackedItem:
    """Endpoint to create a new tracked item."""
    # Ensure we have a unique slug
    unique_slug = generate_unique_slug(session, item.get_slug, TrackedItem)

    db_item = TrackedItem(
        name=item.name,
        slug=unique_slug,
        location=item.location,
        notes=item.notes,
        attributes=item.attributes,
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("/{slug}", response_model=TrackedItemResponse)
def get_tracked_item(slug: str, session: Session = Depends(get_db)) -> TrackedItem:
    """Endpoint to get a tracked item by its slug."""
    item = session.query(TrackedItem).filter_by(slug=slug).first()
    if not item:
        logger.warning(f"Tracked item with slug '{slug}' not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracked item not found")
    return item


@router.patch("/{slug}", response_model=TrackedItemResponse)
def update_tracked_item(
    slug: str,
    item_update: TrackedItemCreateRequest,
    update_slug: bool = False,
    session: Session = Depends(get_db),
) -> TrackedItem:
    """Endpoint to update an existing tracked item."""
    item = session.query(TrackedItem).filter_by(slug=slug).first()
    if not item:
        logger.warning(f"Tracked item with slug '{slug}' not found for update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracked item not found")

    # Update fields
    item.name = item_update.name
    item.location = item_update.location
    item.notes = item_update.notes
    item.attributes = item_update.attributes

    # Handle slug update if provided
    if update_slug or item_update.slug:
        if not item_update.slug:
            # If slug is not provided but update_slug is True, generate a new slug from the name
            item_update.slug = slugify(item_update.name)
        unique_slug = generate_unique_slug(session, item_update.get_slug, TrackedItem)
        item.slug = unique_slug

    session.commit()
    session.refresh(item)
    return item


@router.delete("/{slug}", response_model=BaseDetailResponse)
def delete_tracked_item(slug: str, session: Session = Depends(get_db)) -> dict[str, str]:
    """Endpoint to delete a tracked item by its slug."""
    item = session.query(TrackedItem).filter_by(slug=slug).first()
    if not item:
        logger.warning(f"Tracked item with slug '{slug}' not found for deletion")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tracked item not found")

    item_name = item.name

    session.delete(item)
    session.commit()
    return {"detail": f"Tracked item '{item_name}' deleted successfully"}
