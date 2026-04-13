"""Created by upkeeper.devtools.create_module."""

from collections.abc import Generator

from pydantic import AnyUrl
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from upkeeper.logging_config import get_logger

from .settings import settings

logger = get_logger(__name__)


def is_sqlite(url: AnyUrl) -> bool:
    return url.scheme in ("sqlite", "sqlite3")


engine_kwargs: dict[str, bool | dict[str, bool]] = {"echo": settings.debug}

if is_sqlite(settings.database_url):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

logger.debug(
    f"Creating database engine with URL: {settings.database_url} and kwargs: {engine_kwargs}"
)

engine = create_engine(str(settings.database_url), **engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """Yields a database session and ensures it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
