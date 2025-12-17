from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from songs_api.api.errors import ApiError
from songs_api.schemas import (
    AddRatingRequest,
    LoginRequest,
    LoginResponse,
    PaginationQueryParams,
    SearchQueryParams,
)
from songs_api.security.jwt_auth import requires_jwt_auth
from songs_api.services import AuthService, RatingsService, SongsService
from songs_api.utils.validation import validate_query, validate_request


def register_routes(bp: Blueprint) -> None:
    """Register all v1 API routes."""

    @bp.route("/health", methods=["GET"])
    def health():
        """
        Health check endpoint
        ---
        tags:
          - Health
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

    @bp.route("/auth/login", methods=["POST"])
    @validate_request(LoginRequest)
    def login(data: LoginRequest):
        """
        Login to obtain JWT access token
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: admin
                password:
                  type: string
                  example: admin
        responses:
          200:
            description: Successfully authenticated
            schema:
              type: object
              properties:
                access_token:
                  type: string
                token_type:
                  type: string
                  example: bearer
          401:
            description: Invalid credentials
          422:
            description: Validation error
        """
        admin_username = str(current_app.config.get("ADMIN_USERNAME", "admin"))
        admin_password = str(current_app.config.get("ADMIN_PASSWORD", "admin"))

        auth_service = AuthService(admin_username=admin_username, admin_password=admin_password)
        access_token = auth_service.login(username=data.username, password=data.password)

        response = LoginResponse(access_token=access_token, token_type="bearer")
        return jsonify(response.model_dump())

    @bp.route("/songs", methods=["GET"])
    @requires_jwt_auth
    @validate_query(PaginationQueryParams)
    def list_songs(query: PaginationQueryParams):
        """
        List songs with pagination
        ---
        tags:
          - Songs
        security:
          - Bearer: []
        parameters:
          - in: query
            name: page
            type: integer
            default: 1
            description: Page number
          - in: query
            name: page_size
            type: integer
            default: 20
            description: Number of items per page (max 100)
        responses:
          200:
            description: Paginated list of songs
          401:
            description: Unauthorized - missing or invalid JWT token
          422:
            description: Validation error
        """
        songs_service = SongsService()
        response = songs_service.list_songs(page=query.page, page_size=query.page_size)
        return jsonify(response.model_dump())

    @bp.route("/songs/difficulty/average", methods=["GET"])
    @requires_jwt_auth
    def average_difficulty():
        """
        Get average difficulty of songs, optionally filtered by level
        ---
        tags:
          - Songs
        security:
          - Bearer: []
        parameters:
          - in: query
            name: level
            type: integer
            required: false
            description: Filter by difficulty level
        responses:
          200:
            description: Average difficulty
          401:
            description: Unauthorized
        """
        level_str = request.args.get("level")
        level: int | None = None
        if level_str:
            try:
                level = int(level_str)
            except ValueError as exc:
                raise ApiError(message="Invalid integer for 'level'", status_code=400) from exc

        songs_service = SongsService()
        response = songs_service.get_average_difficulty(level=level)
        return jsonify(response.model_dump())

    @bp.route("/songs/search", methods=["GET"])
    @requires_jwt_auth
    @validate_query(SearchQueryParams)
    def search_songs(query: SearchQueryParams):
        """
        Search songs by artist or title
        ---
        tags:
          - Songs
        security:
          - Bearer: []
        parameters:
          - in: query
            name: message
            type: string
            required: true
            description: Search query for artist or title
          - in: query
            name: page
            type: integer
            default: 1
          - in: query
            name: page_size
            type: integer
            default: 20
        responses:
          200:
            description: Search results with pagination
          400:
            description: Bad request - missing message parameter
          401:
            description: Unauthorized
          422:
            description: Validation error
        """
        songs_service = SongsService()
        response = songs_service.search_songs(
            message=query.message,
            page=query.page,
            page_size=query.page_size,
        )
        return jsonify(response.model_dump())

    @bp.route("/songs/ratings", methods=["POST"])
    @requires_jwt_auth
    @validate_request(AddRatingRequest)
    def add_rating(data: AddRatingRequest):
        """
        Add a rating for a song
        ---
        tags:
          - Ratings
        security:
          - Bearer: []
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                song_id:
                  type: string
                  description: MongoDB ObjectId of the song
                rating:
                  type: integer
                  minimum: 1
                  maximum: 5
        responses:
          201:
            description: Rating added successfully
          400:
            description: Invalid request body
          401:
            description: Unauthorized
          404:
            description: Song not found
          422:
            description: Validation error
        """
        ratings_service = RatingsService()
        response = ratings_service.add_rating(song_id=data.song_id, rating=data.rating)
        return jsonify(response.model_dump()), 201

    @bp.route("/songs/<song_id>/ratings", methods=["GET"])
    @requires_jwt_auth
    def get_rating_stats(song_id: str):
        """
        Get rating statistics for a song
        ---
        tags:
          - Ratings
        security:
          - Bearer: []
        parameters:
          - in: path
            name: song_id
            type: string
            required: true
            description: MongoDB ObjectId of the song
        responses:
          200:
            description: Rating statistics
          401:
            description: Unauthorized
          404:
            description: Song not found
        """
        ratings_service = RatingsService()
        response = ratings_service.get_rating_stats(song_id=song_id)
        return jsonify(response.model_dump())
