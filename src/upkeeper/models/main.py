"""Created by upkeeper.devtools.create_module."""

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

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
