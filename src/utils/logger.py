"""
Structured JSON logger for DERMS.

Wraps the standard Python ``logging`` module with ``python-json-logger``
to emit structured JSON log records suitable for aggregation by tools
such as Datadog, Grafana Loki, or AWS CloudWatch.
"""

from __future__ import annotations

import logging
import sys

from pythonjsonlogger import jsonlogger  # type: ignore[import]

_LOGGER_CACHE: dict[str, logging.Logger] = {}


def get_logger(name: str, level: str | None = None) -> logging.Logger:
    """Return a structured JSON logger for the given module name.

    Loggers are cached so repeated calls with the same ``name`` return the
    same instance without adding duplicate handlers.

    Args:
        name: Typically ``__name__`` of the calling module.
        level: Optional log level override (e.g. ``"DEBUG"``). Defaults to
            the value of the ``LOG_LEVEL`` environment variable, falling back
            to ``"INFO"``.

    Returns:
        Configured :class:`logging.Logger` instance.
    """
    if name in _LOGGER_CACHE:
        return _LOGGER_CACHE[name]

    import os

    effective_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()

    logger = logging.getLogger(name)
    logger.setLevel(effective_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(effective_level)
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False

    _LOGGER_CACHE[name] = logger
    return logger
