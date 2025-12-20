"""System-related routes (health checks, status, etc.)."""

from __future__ import annotations

from flask import Blueprint, jsonify


def register_system_routes(bp: Blueprint) -> None:
    """Register system-related routes."""

    @bp.route("/health", methods=["GET"])
    def health():
        """
        Health check endpoint
        ---
        tags:
          - System
        responses:
          200:
            description: Service is healthy
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: healthy
        """
        return jsonify({"status": "healthy"})
