# pyright: reportCallInDefaultInitializer=false
# ruff: noqa: B008
"""Created by upkeeper.devtools.create_module."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from upkeeper.core import JSONDict, slugify
from upkeeper.database import get_db
from upkeeper.logging_config import get_logger
from upkeeper.models.base import generate_unique_slug
from upkeeper.models.main import TrackedItem

logger = get_logger(__name__)


router = APIRouter(prefix="/items", tags=["items"])


class TrackedItemResponse(BaseModel):
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
