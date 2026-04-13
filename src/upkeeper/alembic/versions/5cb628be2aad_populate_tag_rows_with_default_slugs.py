"""populate Tag rows with default slugs

Revision ID: 5cb628be2aad
Revises: d0774f8030a9
Create Date: 2026-04-13 15:50:13.459258

"""
# pyright: reportUnusedCallResult=false

import logging
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from upkeeper.core import slugify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision: str = "5cb628be2aad"
down_revision: str | Sequence[str] | None = "d0774f8030a9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Populate slug column for existing Tag rows using the name column
    connection = op.get_bind()

    # Get all existing tag records
    result = connection.execute(sa.text("SELECT id, name FROM tag WHERE slug IS NULL"))
    tag_rows = result.fetchall()

    if not tag_rows:
        logger.warning("No Tag rows found without slugs. Skipping slug population.")
        return

    logger.info(f"Found {len(tag_rows)} Tag rows without slugs. Populating slugs...")

    # Update each row with a generated slug
    for tag_id, name in tag_rows:  # pyright: ignore[reportAny]
        slug_value = slugify(name)  # pyright: ignore[reportAny]

        # Handle potential slug conflicts by appending a counter if needed
        counter = 1
        unique_slug = slug_value
        while True:
            # Check if this slug already exists
            check_result = connection.execute(
                sa.text("SELECT COUNT(*) FROM tag WHERE slug = :slug"), {"slug": unique_slug}
            )
            if check_result.scalar() == 0:
                break
            unique_slug = f"{slug_value}-{counter}"
            counter += 1
            if counter > 1000:  # Safety check to prevent infinite loop
                raise RuntimeError(f"Could not generate unique slug for tag '{name}'")

        # Update the row with the unique slug
        connection.execute(
            sa.text("UPDATE tag SET slug = :slug WHERE id = :id"),
            {"slug": unique_slug, "id": tag_id},
        )


def downgrade() -> None:
    """Downgrade schema."""
    # This downgrade does not revert the slug values to NULL, as that would result in data loss.
    pass
