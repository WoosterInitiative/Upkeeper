"""Created by upkeeper.devtools.create_module."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from upkeeper.logging_config import get_logger

logger = get_logger(__name__)


class BaseAPI(BaseModel):
    model_config: ConfigDict = ConfigDict(alias_generator=to_camel, populate_by_name=True)  # pyright: ignore[reportIncompatibleVariableOverride]


class TimestampResponseMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class BaseDetailResponse(BaseAPI):
    detail: str
