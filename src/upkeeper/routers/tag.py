# pyright: reportCallInDefaultInitializer=false
# ruff: noqa: B008
"""Created by upkeeper.devtools.create_module."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from upkeeper.core import slugify
from upkeeper.database import get_db
from upkeeper.logging_config import get_logger
from upkeeper.models.base import generate_unique_slug
from upkeeper.models.main import ItemTag, Tag, TrackedItem
from upkeeper.routers.base import BaseDetailResponse
from upkeeper.routers.entry import LogEntryResponse
from upkeeper.routers.tracked_item import TrackedItemResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/tags", tags=["tags"])


class TagResponse(BaseModel):
    id: int
    name: str
    slug: str


class TagCreateRequest(BaseModel):
    name: Annotated[str, Field(max_length=50)]
    slug: Annotated[str | None, Field(max_length=100)] = None

    @property
    def get_slug(self) -> str:
        """Get the slug value, ensuring it is generated if not explicitly set."""
        return self.slug or slugify(self.name)


class LogTagResponse(BaseModel):
    tag_id: int
    log_entry_id: int


class LogTagResponseExtra(LogTagResponse):
    log_entry: LogEntryResponse
    tag: TagResponse


class ItemTagResponse(BaseModel):
    tracked_item_id: int
    tag_id: int


class ItemTagResponseExtra(ItemTagResponse):
    tracked_item: TrackedItemResponse
    tag: TagResponse


class ItemTagCreateRequest(BaseModel):
    tracked_item_id: int
    tag_id: int


@router.get("", response_model=list[TagResponse])
def list_tags(session: Session = Depends(get_db)) -> list[Tag]:
    """Endpoint to list all tags."""
    return session.query(Tag).all()


@router.post("", response_model=TagResponse)
def create_tag(tag: TagCreateRequest, session: Session = Depends(get_db)) -> Tag:
    """Endpoint to create a new tag."""
    unique_slug = generate_unique_slug(session, tag.get_slug, Tag)
    db_tag = Tag(name=tag.name, slug=unique_slug)  # , slug=unique_slug)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag


@router.get("/{slug}", response_model=TagResponse)
def get_tag(slug: str, session: Session = Depends(get_db)) -> Tag:
    """Endpoint to retrieve a tag by its slug."""
    db_tag = session.query(Tag).filter(Tag.slug == slug).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag


@router.patch("/{slug}", response_model=TagResponse)
def update_tag(
    slug: str,
    tag_update: TagCreateRequest,
    update_slug: bool = False,
    session: Session = Depends(get_db),
) -> Tag:
    """Endpoint to update an existing tag."""
    db_tag = session.query(Tag).filter(Tag.slug == slug).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Update the tag's name and slug
    db_tag.name = tag_update.name
    # Handle slug update if provided
    if update_slug or tag_update.slug:
        if not tag_update.slug:
            # If slug is not provided but update_slug is True, generate a new slug from the name
            tag_update.slug = slugify(tag_update.name)
        unique_slug = generate_unique_slug(session, tag_update.get_slug, Tag)
        db_tag.slug = unique_slug

    session.commit()
    session.refresh(db_tag)
    return db_tag


@router.delete("/{slug}", response_model=BaseDetailResponse)
def delete_tag(slug: str, session: Session = Depends(get_db)) -> dict[str, str]:
    """Endpoint to delete a tag by its slug."""
    db_tag = session.query(Tag).filter(Tag.slug == slug).first()
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    session.delete(db_tag)
    session.commit()
    return {"detail": "Tag deleted successfully"}


# @router.get("", response_model=list[ItemTagResponse])
# def list_item_tags(session: Session = Depends(get_db)) -> list[ItemTag]:
#     """Endpoint to list all item tags."""
#     return session.query(ItemTag).all()
