"""Application constants and enums."""

from __future__ import annotations

from enum import Enum


class LogFormat(str, Enum):
    """Log output format options."""

    TEXT = "text"
    JSON = "json"


class LogLevel(str, Enum):
    """Logging level options."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TokenType(str, Enum):
    """JWT token type."""

    BEARER = "bearer"


class RatingRange:
    """Rating value constraints."""

    MIN = 1
    MAX = 5


class PaginationDefaults:
    """Default pagination values."""

    PAGE = 1
    PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


class SwaggerConfig:
    """Swagger/OpenAPI configuration constants."""

    ENDPOINT = "apispec"
    ROUTE = "/apispec.json"
    STATIC_URL_PATH = "/flasgger_static"
    SPECS_ROUTE = "/docs"


class JWTClaim(str, Enum):
    """JWT token claim names."""

    SUBJECT = "sub"
    EXPIRATION = "exp"
    ISSUED_AT = "iat"


class HTTPStatusCode(int, Enum):
    """HTTP status codes."""

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
