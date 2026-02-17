"""
Structured JSON logging with request-ID middleware.
Usage:
    from services.logging_service import get_logger, init_request_logging
    logger = get_logger(__name__)
    init_request_logging(app)   # call once at app startup
"""

import logging
import uuid

from flask import Flask, g, request
from pythonjsonlogger.json import JsonFormatter


def get_logger(name: str) -> logging.Logger:
    """Return a JSON-formatted logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"asctime": "timestamp", "levelname": "level"},
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def init_request_logging(app: Flask) -> None:
    """Attach request-ID middleware and request/response logging."""
    logger = get_logger("http")

    @app.before_request
    def _set_request_id():
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])

    @app.after_request
    def _log_request(response):
        logger.info(
            "request",
            extra={
                "request_id": getattr(g, "request_id", "-"),
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "remote_addr": request.remote_addr,
            },
        )
        response.headers["X-Request-ID"] = getattr(g, "request_id", "-")
        return response
