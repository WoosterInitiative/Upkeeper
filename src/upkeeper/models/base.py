"""Created by upkeeper.devtools.create_module."""

from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, MappedColumn, Session, mapped_column

from upkeeper.logging_config import get_logger
from upkeeper.settings import settings

logger = get_logger(__name__)


class Base(DeclarativeBase):
    pass


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)

Base.metadata = metadata


class TimestampMixin:
    created_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


def generate_unique_slug(
    session: Session,
    base_slug: str,
    model_cls: type[Base],
    *,
    slug_field: str = "slug",
    max_counter: int = settings.max_slug_counter,
) -> str:
    """Generate a unique slug by appending a number if necessary.

    Args:
        session: Database session to use for checking existing slugs.
        base_slug: The initial slug to start with.
        model_cls: The SQLAlchemy model class to check for existing slugs.
        slug_field: The name of the slug field in the model (default "slug").
        max_counter: Maximum number of attempts to find a unique slug before giving up.

    Returns:
        A unique slug string.

    Raises:
        HTTPException: If a unique slug cannot be generated within the max_counter limit.
    """
    slug = base_slug
    counter = 1

    while True:
        # Check if slug already exists
        existing = session.query(model_cls).filter(getattr(model_cls, slug_field) == slug).first()
        if not existing:
            return slug

        # Generate new slug with counter
        slug = f"{base_slug}-{counter}"
        counter += 1

        # Prevent infinite loops - reasonable upper limit
        if counter > settings.max_slug_counter:
            raise HTTPException(
                status_code=500,
                detail=f"Unable to generate unique slug after {max_counter} attempts",
            )
