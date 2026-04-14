# pyright: reportCallInDefaultInitializer=false
# ruff: noqa: B008
"""Created by upkeeper.devtools.create_module."""

from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from upkeeper.logging_config import get_logger
from upkeeper.routers.base import BaseAPI

from ..database import get_db

logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


class HealthCheckResponse(BaseAPI):
    status: Literal["ok"]


@router.get("", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    _ = db.execute(text("SELECT 1"))
    return {"status": "ok"}
