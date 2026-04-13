"""Created by upkeeper.devtools.create_module."""

from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI

# Import setup_logging instead of set_log_level and call it first
from upkeeper.logging_config import get_logger, setup_logging

from .routers import entry, health, tag, tracked_item
from .settings import VERSION, settings

# Setup logging before any other imports that might use loggers
setup_logging()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # pyright: ignore[reportUnusedParameter]
    # Run Alembic migrations on startup
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations completed")
    yield


def create_app() -> FastAPI:
    """Factory function to create and configure the FastAPI app."""
    app = FastAPI(title=settings.app_name, version=VERSION, debug=settings.debug, lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(tracked_item.router)
    app.include_router(entry.router)
    app.include_router(tag.router)
    return app


app = create_app()
