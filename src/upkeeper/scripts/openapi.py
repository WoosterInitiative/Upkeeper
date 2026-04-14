"""Created by upkeeper.devtools.create_module."""

import json
from collections.abc import Callable
from typing import BinaryIO, cast

from fastapi import FastAPI

from upkeeper.core import JSONDict
from upkeeper.logging_config import get_logger
from upkeeper.main import create_app

logger = get_logger(__name__)

type OpenAPISpec = JSONDict


class OpenAPIGenerator:
    """Class to generate OpenAPI specification for the FastAPI application."""

    _spec: OpenAPISpec | None = None
    _processed_for_client: bool | None = None

    def __init__(self, app_factory: Callable[[], FastAPI] = create_app):
        self.app_factory: Callable[[], FastAPI] = app_factory

    def get_spec(self) -> OpenAPISpec:
        if self._spec is None:
            app = self.app_factory()
            self._spec = app.openapi()
            self._processed_for_client = False
            logger.info("OpenAPI specification generated successfully")
        return self._spec

    def process_spec_for_client(self) -> None:
        """Process the OpenAPI spec for client consumption, if needed."""
        spec = self._spec
        if spec is None:
            spec = self.get_spec()

        spec_paths = cast("JSONDict", spec.get("paths", {}))

        for path_data in spec_paths.values():
            path_data = cast("JSONDict", path_data)
            for operation in path_data.values():
                operation = cast("JSONDict", operation)
                tags = cast("list[JSONDict]", operation.get("tags"))
                tag = tags[0]
                operation_id = cast("str", operation.get("operationId"))
                to_remove = f"{tag}-"
                new_operation_id = operation_id[len(to_remove) :]
                operation["operationId"] = new_operation_id

        spec["paths"] = spec_paths
        self._spec = spec
        self._processed_for_client = True

        logger.info("OpenAPI specification processed for client")

    def get_client_spec(self) -> OpenAPISpec:
        spec = self.get_spec()
        if not self._processed_for_client:
            # Here you can modify the spec if needed before sending to client
            # For example, you could remove internal endpoints or add custom metadata
            self._processed_for_client = True
            logger.info("OpenAPI specification processed for client")
        return spec
