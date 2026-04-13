"""Created by upkeeper.devtools.create_module."""

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from upkeeper.core import JSONDict
from upkeeper.logging_config import get_logger

from .base import Base, TimestampMixin

logger = get_logger(__name__)


class TrackedItem(Base, TimestampMixin):
    __tablename__ = "tracked_item"  # pyright: ignore[reportUnannotatedClassAttribute]

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attributes: Mapped[JSONDict] = mapped_column(JSON, default=dict)

    # Relationship to access related log entries
    log_entries: Mapped[list["LogEntry"]] = relationship("LogEntry", back_populates="tracked_item")
    tags: Mapped[list["ItemTag"]] = relationship("ItemTag", back_populates="tracked_item")


class LogEntry(Base, TimestampMixin):
    __tablename__ = "log_entry"  # pyright: ignore[reportUnannotatedClassAttribute]

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tracked_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tracked_item.id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    details: Mapped[JSONDict] = mapped_column(JSON, default=dict)
    performed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    # Relationship to access the parent tracked item
    tracked_item: Mapped["TrackedItem"] = relationship("TrackedItem", back_populates="log_entries")
    tags: Mapped[list["LogTag"]] = relationship("LogTag", back_populates="log_entry")


class Tag(Base):
    __tablename__ = "tag"  # pyright: ignore[reportUnannotatedClassAttribute]

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    log_tags: Mapped[list["LogTag"]] = relationship("LogTag", back_populates="tag")


class LogTag(Base):
    __tablename__ = "log_tag"  # pyright: ignore[reportUnannotatedClassAttribute]

    tag_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    )
    tag: Mapped["Tag"] = relationship("Tag", back_populates="log_tags")

    log_entry_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("log_entry.id", ondelete="CASCADE"), primary_key=True
    )
    log_entry: Mapped["LogEntry"] = relationship("LogEntry", back_populates="tags")


class ItemTag(Base):
    __tablename__ = "item_tag"  # pyright: ignore[reportUnannotatedClassAttribute]

    tracked_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tracked_item.id", ondelete="CASCADE"), primary_key=True
    )
    tracked_item: Mapped["TrackedItem"] = relationship("TrackedItem", back_populates="item_tags")

    tag_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    )
    tag: Mapped["Tag"] = relationship("Tag", back_populates="item_tags")
