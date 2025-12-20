from __future__ import annotations

from dataclasses import dataclass

from flask import jsonify

from songs_api.constants import HTTPStatusCode


@dataclass(frozen=True)
class ApiError(Exception):
    """Base API error with an HTTP status code."""

    message: str
    status_code: int = HTTPStatusCode.BAD_REQUEST

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True)
class BadRequestError(ApiError):
    """400 Bad Request error."""

    status_code: int = HTTPStatusCode.BAD_REQUEST


@dataclass(frozen=True)
class UnauthorizedError(ApiError):
    """401 Unauthorized error."""

    status_code: int = HTTPStatusCode.UNAUTHORIZED


@dataclass(frozen=True)
class NotFoundError(ApiError):
    """404 Not Found error."""

    status_code: int = HTTPStatusCode.NOT_FOUND


@dataclass(frozen=True)
class ConflictError(ApiError):
    """409 Conflict error."""

    status_code: int = HTTPStatusCode.CONFLICT


@dataclass(frozen=True)
class ValidationError(ApiError):
    """422 Validation error."""

    status_code: int = HTTPStatusCode.UNPROCESSABLE_ENTITY


@dataclass(frozen=True)
class InternalServerError(ApiError):
    """500 Internal Server error."""

    status_code: int = HTTPStatusCode.INTERNAL_SERVER_ERROR


def json_error(err: ApiError) -> tuple:
    """Serialize an ApiError to a JSON response."""
    resp = jsonify({"error": err.message})
    if err.status_code == HTTPStatusCode.UNAUTHORIZED:
        resp.headers["WWW-Authenticate"] = 'Bearer realm="Songs API"'
    return resp, err.status_code
