"""Songs-related routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from songs_api.api.caching import cached_response
from songs_api.api.errors import BadRequestError
from songs_api.schemas import (
    AddRatingRequest,
    PaginationQueryParams,
    SearchQueryParams,
)
from songs_api.security.jwt_auth import requires_jwt_auth
from songs_api.services import RatingsService, SongsService
from songs_api.utils.dependencies import inject
from songs_api.utils.validation import validate_query, validate_request


def register_songs_routes(bp: Blueprint) -> None:
    """Register songs-related routes."""

    @bp.route("/songs", methods=["GET"])
    @requires_jwt_auth
    @validate_query(PaginationQueryParams)
    @cached_response("songs:list", ttl=300)
    @inject(SongsService)
    def list_songs(query: PaginationQueryParams, songs_service: SongsService):
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
        response = songs_service.list_songs(page=query.page, page_size=query.page_size)
        return jsonify(response.model_dump())

    @bp.route("/songs/difficulty/average", methods=["GET"])
    @requires_jwt_auth
    @cached_response("songs:avg_difficulty", ttl=600)
    @inject(SongsService)
    def average_difficulty(songs_service: SongsService):
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
                raise BadRequestError(message="Invalid integer for 'level'") from exc

        response = songs_service.get_average_difficulty(level=level)
        return jsonify(response.model_dump())

    @bp.route("/songs/search", methods=["GET"])
    @requires_jwt_auth
    @validate_query(SearchQueryParams)
    @cached_response("songs:search", ttl=600)
    @inject(SongsService)
    def search_songs(query: SearchQueryParams, songs_service: SongsService):
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
        response = songs_service.search_songs(
            message=query.message,
            page=query.page,
            page_size=query.page_size,
        )
        return jsonify(response.model_dump())

    @bp.route("/songs/ratings", methods=["POST"])
    @requires_jwt_auth
    @validate_request(AddRatingRequest)
    @inject(RatingsService)
    def add_rating(data: AddRatingRequest, ratings_service: RatingsService):
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
        response = ratings_service.add_rating(song_id=data.song_id, rating=data.rating)
        return jsonify(response.model_dump()), 201

    @bp.route("/songs/<song_id>/ratings", methods=["GET"])
    @requires_jwt_auth
    @cached_response("ratings:stats", ttl=300)
    @inject(RatingsService)
    def get_rating_stats(ratings_service: RatingsService, song_id: str):
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
        response = ratings_service.get_rating_stats(song_id=song_id)
        return jsonify(response.model_dump())
