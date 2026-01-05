import logging
from typing import TYPE_CHECKING

import pytest

from upkeeper import logging_config
from upkeeper.settings import Settings

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture(autouse=True)
def clear_env(monkeypatch: MonkeyPatch):
    """Clear LOG_LEVEL env var before each test."""
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)


def test_default_level_info():
    """Without overrides, should default to INFO."""
    s = Settings()
    assert s.default_log_level == logging.INFO


def test_debug_env_sets_debug(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("DEBUG", "true")
    s = Settings()
    assert s.default_log_level == logging.DEBUG


def test_loglevel_env_override(monkeypatch: MonkeyPatch):
    """LOGLEVEL overrides both default and DEBUG."""
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("LOG_LEVEL", "TRACE")
    s = Settings()
    # TRACE resolves to 5
    assert getattr(logging, s.log_level.upper()) == 5


def test_setup_logging_trace_level(monkeypatch: MonkeyPatch, caplog):
    """TRACE level works and produces output."""
    monkeypatch.setenv("LOG_LEVEL", "TRACE")

    logging_config.setup_logging()  # pyright: ignore[reportUnknownMemberType]
    log = logging.getLogger("test")

    with caplog.at_level(logging_config.TRACE_LEVEL_NUM):
        log.trace("trace message")

    assert "trace message" in caplog.text
