from __future__ import annotations

from flask import Blueprint

from songs_api.api.v1.routes import register_routes

v1_bp = Blueprint("v1", __name__, url_prefix="/api/v1")

register_routes(v1_bp)



