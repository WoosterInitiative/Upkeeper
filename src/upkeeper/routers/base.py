"""Created by upkeeper.devtools.create_module."""

from datetime import datetime

from pydantic import BaseModel

from upkeeper.logging_config import get_logger

logger = get_logger(__name__)


class TimestampResponseMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class BaseDetailResponse(BaseModel):
    detail: str
