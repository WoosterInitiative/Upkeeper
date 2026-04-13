# pyright: reportCallInDefaultInitializer=false
# ruff: noqa: B008
"""Created by upkeeper.devtools.create_module."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from upkeeper.core import JSONDict
from upkeeper.database import get_db
from upkeeper.logging_config import get_logger
from upkeeper.models.main import LogEntry
from upkeeper.routers.base import BaseDetailResponse, TimestampResponseMixin
from upkeeper.routers.tracked_item import TrackedItemResponse

logger = get_logger(__name__)


router = APIRouter(prefix="/entries", tags=["entries"])


class LogEntryResponse(TimestampResponseMixin):
    id: int
    tracked_item_id: int
    action: str
    notes: str | None = None
    performed_at: datetime
    details: JSONDict
    tags: list[str] = Field(default_factory=list)


class LogEntryExtraResponse(LogEntryResponse):
    tracked_item: TrackedItemResponse


class LogEntryCreateRequest(BaseModel):
    tracked_item_id: int
    action: Annotated[str, Field(min_length=1, max_length=255)]
    notes: Annotated[str | None, Field(max_length=255)] = None
    details: JSONDict
    performed_at: datetime | None = None


@router.get("", response_model=list[LogEntryResponse])
def list_log_entries(session: Session = Depends(get_db)) -> list[LogEntry]:
    """Endpoint to list all log entries."""
    return session.query(LogEntry).all()


@router.post("", response_model=LogEntryResponse)
def create_log_entry(entry: LogEntryCreateRequest, session: Session = Depends(get_db)) -> LogEntry:
    """Endpoint to create a new log entry."""
    db_entry = LogEntry(
        action=entry.action,
        tracked_item_id=entry.tracked_item_id,
        notes=entry.notes,
        details=entry.details,
        performed_at=entry.performed_at or datetime.now(),
    )
    session.add(db_entry)
    session.commit()
    session.refresh(db_entry)
    return db_entry


@router.get("/{entry_id}", response_model=LogEntryResponse | LogEntryExtraResponse)
def get_log_entry(
    entry_id: int,
    extra: Annotated[list[str] | None, Query()] = None,
    session: Session = Depends(get_db),
) -> LogEntry:
    """Endpoint to get a log entry by ID, with optional extra data."""
    query = session.query(LogEntry).filter(LogEntry.id == entry_id)

    if extra and "tracked_item" in extra:
        query = query.options(joinedload(LogEntry.tracked_item))

    db_entry = query.first()
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log entry not found")

    return db_entry


@router.patch("/{entry_id}", response_model=LogEntryResponse)
def update_log_entry(
    entry_id: int, entry: LogEntryCreateRequest, session: Session = Depends(get_db)
) -> LogEntry:
    """Endpoint to update an existing log entry."""
    db_entry = session.query(LogEntry).filter(LogEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log entry not found")

    db_entry.action = entry.action
    db_entry.notes = entry.notes
    db_entry.details = entry.details
    db_entry.performed_at = entry.performed_at or db_entry.performed_at

    session.commit()
    session.refresh(db_entry)
    return db_entry


@router.delete("/{entry_id}", response_model=BaseDetailResponse)
def delete_log_entry(entry_id: int, session: Session = Depends(get_db)) -> dict[str, str]:
    """Endpoint to delete a log entry."""
    db_entry = session.query(LogEntry).filter(LogEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log entry not found")

    session.delete(db_entry)
    session.commit()
    return {"detail": "Log entry deleted successfully"}
