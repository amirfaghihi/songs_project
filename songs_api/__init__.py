from __future__ import annotations

from flasgger import Swagger
from flask import Flask, jsonify, request
from loguru import logger
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from songs_api.api.errors import ApiError, json_error
from songs_api.api.v1 import v1_bp
from songs_api.database import ensure_indexes, init_db
from songs_api.logging_config import configure_logging
from songs_api.rate_limiter import create_limiter
from songs_api.settings import Settings


def create_app(settings: Settings | None = None) -> Flask:
    """Create and configure the Flask application with MongoDB support."""
    app = Flask(__name__)

    app_settings = settings or Settings()

    # Configure logging
    configure_logging(app_settings)
    logger.info(f"Starting Songs API in {app_settings.environment.value} mode")

    app.config["JWT_SECRET_KEY"] = app_settings.jwt_secret_key
    app.config["JWT_ALGORITHM"] = app_settings.jwt_algorithm
    app.config["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = app_settings.jwt_access_token_expire_minutes
    app.config["ADMIN_USERNAME"] = app_settings.admin_username
    app.config["ADMIN_PASSWORD"] = app_settings.admin_password
    app.config["MONGO_URI"] = app_settings.mongo_uri
    app.config["MONGO_DB_NAME"] = app_settings.mongo_db_name
    app.config["SONGS_JSON_PATH"] = app_settings.songs_json_path
    app.config["SETTINGS"] = app_settings

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs",
    }

    swagger_template = {
        "info": {
            "title": app_settings.api_title,
            "description": "Production-level REST API for songs and ratings management",
            "version": app_settings.api_version,
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using Bearer scheme. Example: 'Bearer {token}'",
            }
        },
        "security": [{"Bearer": []}],
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    # Initialize rate limiter
    limiter = create_limiter(app, app_settings)
    app.extensions["limiter"] = limiter

    init_db(mongo_uri=app_settings.mongo_uri, db_name=app_settings.mongo_db_name)

    # Request logging middleware
    @app.before_request
    def log_request():
        """Log incoming requests."""
        logger.info(f"{request.method} {request.path}", extra={"remote_addr": request.remote_addr})

    @app.after_request
    def log_response(response):
        """Log outgoing responses."""
        logger.info(
            f"{request.method} {request.path} - {response.status_code}",
            extra={"status_code": response.status_code, "remote_addr": request.remote_addr},
        )
        return response

    @app.errorhandler(ValidationError)
    def _handle_pydantic_validation_error(err: ValidationError):
        """Centralized Pydantic ValidationError handler."""
        logger.warning(f"Validation error: {err.errors()}")
        return jsonify({"errors": err.errors()}), 422

    @app.errorhandler(ApiError)
    def _handle_api_error(err: ApiError):
        logger.error(f"API error: {err.message}", extra={"status_code": err.status_code})
        return json_error(err)

    @app.errorhandler(HTTPException)
    def _handle_http_error(err: HTTPException):
        logger.error(f"HTTP error: {err.description}", extra={"status_code": err.code})
        return json_error(ApiError(message=err.description or "Error", status_code=err.code or 500))

    app.register_blueprint(v1_bp)

    @app.teardown_appcontext
    def _teardown(_: object | None) -> None:
        pass

    @app.cli.command("init-db")
    def _init_db():
        """Initialize database connection and ensure indexes."""
        ensure_indexes()
        print("Database initialized and indexes created.")

    @app.cli.command("seed-songs")
    def _seed_songs():
        """Seed songs from songs.json file."""
        from songs_api.scripts.seed import seed_songs_from_file

        seed_songs_from_file(app.config["SONGS_JSON_PATH"])

    return app
