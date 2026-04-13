"""Project level core functionality that doesn't fit into a more specific module."""

import re
import unicodedata
from dataclasses import dataclass
from os import PathLike
from typing import Protocol, override

from typer import Context

from .logging_config import get_logger, set_log_level

logger = get_logger(__name__)

# A type alias for inputs that can be either a string or a PathLike object representing a filesystem path. This is used for type annotations in functions that accept file paths, allowing for flexibility in the types of path inputs while maintaining type safety.
type PathInput = PathLike[str] | str

type JSONValue = str | int | float | bool | None | list["JSONValue"] | JSONDict
type JSONDict = dict[str, JSONValue]


@dataclass
class GlobalCLIOptions:
    verbosity: int
    dry_run: bool = False

    def __post_init__(self) -> None:
        set_log_level(self.verbosity)


class ProjectContext(Context):
    """Custom Typer Context that adds the proper typing for `obj`."""

    obj: GlobalCLIOptions


class HasStr(Protocol):
    @override
    def __str__(self) -> str: ...


# see https://docs.djangoproject.com/en/6.0/ref/utils/#django.utils.text.slugify
def slugify(value: HasStr, *, allow_unicode: bool = False) -> str:
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    logger.debug(f"Slugifying value: {value}")
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    value = re.sub(r"[-\s]+", "-", value).strip("-_")
    logger.debug(f"Slugified value: {value}")
    return value
