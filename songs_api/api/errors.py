from __future__ import annotations

from dataclasses import dataclass

from flask import jsonify


@dataclass(frozen=True)
class ApiError(Exception):
    """API error with an HTTP status code."""

    message: str
    status_code: int = 400


def json_error(err: ApiError):
    """Serialize an ApiError to a JSON response."""
    resp = jsonify({"error": err.message})
    if err.status_code == 401:
        resp.headers["WWW-Authenticate"] = 'Basic realm="Songs API"'
    return resp, err.status_code


