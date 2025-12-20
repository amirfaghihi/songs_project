from __future__ import annotations

from enum import Enum

from flasgger import Swagger
from flask import Flask, jsonify, request
from loguru import logger
from pydantic import ValidationError as PydanticValidationError
from werkzeug.exceptions import HTTPException

from songs_api.api.errors import (
    ApiError,
    BadRequestError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
    json_error,
)
from songs_api.api.v1 import v1_bp
from songs_api.constants import HTTPStatusCode, SwaggerConfig
from songs_api.infrastructure import (
    configure_logging,
    create_limiter,
    ensure_indexes,
    init_cache,
    init_db,
)
from songs_api.settings import Settings


def create_app(settings: Settings | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    app_settings = settings or Settings()

    configure_logging(app_settings)

    cache = init_cache(app_settings)
    if cache.enabled:
        logger.info("Redis cache enabled for production")
    else:
        logger.info("Redis cache disabled (not in production or cache unavailable)")
    env_value = (
        app_settings.environment.value if isinstance(app_settings.environment, Enum) else str(app_settings.environment)
    )
    logger.info(f"Starting Songs API in {env_value} mode")

    app.config["JWT_SECRET_KEY"] = app_settings.jwt_secret_key
    app.config["JWT_ALGORITHM"] = app_settings.jwt_algorithm
    app.config["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = app_settings.jwt_access_token_expire_minutes
    app.config["MONGO_URI"] = app_settings.mongo_uri
    app.config["MONGO_DB_NAME"] = app_settings.mongo_db_name
    app.config["SONGS_JSON_PATH"] = app_settings.songs_json_path
    app.config["SETTINGS"] = app_settings

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": SwaggerConfig.ENDPOINT,
                "route": SwaggerConfig.ROUTE,
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": SwaggerConfig.STATIC_URL_PATH,
        "swagger_ui": True,
        "specs_route": SwaggerConfig.SPECS_ROUTE,
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

    limiter = create_limiter(app, app_settings)
    app.extensions["limiter"] = limiter

    init_db(mongo_uri=app_settings.mongo_uri, db_name=app_settings.mongo_db_name)

    @app.before_request
    def log_request():
        logger.info(f"{request.method} {request.path}", extra={"remote_addr": request.remote_addr})

    @app.after_request
    def log_response(response):
        logger.info(
            f"{request.method} {request.path} - {response.status_code}",
            extra={"status_code": response.status_code, "remote_addr": request.remote_addr},
        )
        return response

    @app.errorhandler(PydanticValidationError)
    def _handle_pydantic_validation_error(err: PydanticValidationError):
        logger.warning(f"Validation error: {err.errors()}")
        return jsonify({"errors": err.errors()}), HTTPStatusCode.UNPROCESSABLE_ENTITY

    @app.errorhandler(BadRequestError)
    @app.errorhandler(UnauthorizedError)
    @app.errorhandler(NotFoundError)
    @app.errorhandler(ConflictError)
    @app.errorhandler(ValidationError)
    @app.errorhandler(InternalServerError)
    @app.errorhandler(ApiError)
    def _handle_api_error(err: ApiError):
        logger.error(f"API error: {err.message}", extra={"status_code": err.status_code})
        return json_error(err)

    @app.errorhandler(HTTPException)
    def _handle_http_error(err: HTTPException):
        logger.error(f"HTTP error: {err.description}", extra={"status_code": err.code})
        status_code = err.code if err.code else HTTPStatusCode.INTERNAL_SERVER_ERROR
        return json_error(ApiError(message=err.description or "Error", status_code=status_code))

    @app.errorhandler(Exception)
    def _handle_generic_error(err: Exception):
        logger.exception(f"Unhandled exception: {str(err)}")
        return json_error(InternalServerError(message="An internal server error occurred. Please try again later."))

    app.register_blueprint(v1_bp)

    @app.teardown_appcontext
    def _teardown(_: object | None) -> None:
        pass

    @app.cli.command("init-db")
    def _init_db():
        ensure_indexes()
        print("Database initialized and indexes created.")

    @app.cli.command("seed-songs")
    def _seed_songs():
        from songs_api.scripts.seed import seed_songs_from_file

        seed_songs_from_file(app.config["SONGS_JSON_PATH"])

    @app.cli.command("seed-users")
    def _seed_users():
        from songs_api.scripts.seed_users import seed_users

        seed_users()

    return app
