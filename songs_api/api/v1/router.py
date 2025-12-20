"""Main routes registration and orchestration."""

from __future__ import annotations

from flask import Blueprint

from songs_api.api.v1.auth_routes import register_auth_routes
from songs_api.api.v1.songs_routes import register_songs_routes
from songs_api.api.v1.system_routes import register_system_routes


def register_routes(bp: Blueprint) -> None:
    """Register all v1 API routes."""
    register_system_routes(bp)
    register_auth_routes(bp)
    register_songs_routes(bp)
