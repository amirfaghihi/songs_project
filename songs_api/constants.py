from __future__ import annotations

from enum import Enum


class LogFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TokenType(str, Enum):
    BEARER = "bearer"


class RatingRange:
    MIN = 1
    MAX = 5


class PaginationDefaults:
    PAGE = 1
    PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


class SwaggerConfig:
    ENDPOINT = "apispec"
    ROUTE = "/apispec.json"
    STATIC_URL_PATH = "/flasgger_static"
    SPECS_ROUTE = "/docs"


class JWTClaim(str, Enum):
    SUBJECT = "sub"
    EXPIRATION = "exp"
    ISSUED_AT = "iat"


class HTTPStatusCode(int, Enum):
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
