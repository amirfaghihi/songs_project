from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_serializer

from songs_api.constants import PaginationDefaults, RatingRange, TokenType


class SongResponse(BaseModel):
    """Song response schema."""

    id: str
    artist: str
    title: str
    difficulty: float
    level: int
    released: date

    @field_serializer("difficulty")
    def serialize_difficulty(self, value: float) -> float:
        """Round difficulty to 3 decimal places."""
        return round(value, 3)


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    page_size: int
    total: int
    total_pages: int


class PaginationQueryParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(default=PaginationDefaults.PAGE, ge=1, description="Page number")
    page_size: int = Field(
        default=PaginationDefaults.PAGE_SIZE,
        ge=1,
        le=PaginationDefaults.MAX_PAGE_SIZE,
        description="Items per page",
    )


class SearchQueryParams(BaseModel):
    """Query parameters for search."""

    message: str = Field(..., min_length=1, description="Search query")
    page: int = Field(default=PaginationDefaults.PAGE, ge=1)
    page_size: int = Field(default=PaginationDefaults.PAGE_SIZE, ge=1, le=PaginationDefaults.MAX_PAGE_SIZE)


class SongsListResponse(BaseModel):
    """Response for paginated songs list."""

    data: list[SongResponse]
    pagination: PaginationMeta


class SearchSongsResponse(BaseModel):
    """Response for songs search."""

    message: str
    data: list[SongResponse]
    pagination: PaginationMeta


class AverageDifficultyResponse(BaseModel):
    """Response for average difficulty."""

    average_difficulty: float | None
    level: int | None

    @field_serializer("average_difficulty")
    def serialize_average_difficulty(self, value: float | None) -> float | None:
        """Round average difficulty to 3 decimal places."""
        return round(value, 3) if value is not None else None


class AddRatingRequest(BaseModel):
    """Request to add a rating."""

    song_id: str
    rating: int = Field(ge=RatingRange.MIN, le=RatingRange.MAX)


class RatingStatsResponse(BaseModel):
    """Response for rating statistics."""

    song_id: str
    average: float | None
    lowest: int | None
    highest: int | None
    count: int

    @field_serializer("average")
    def serialize_average(self, value: float | None) -> float | None:
        """Round average rating to 3 decimal places."""
        return round(value, 3) if value is not None else None


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str
    password: str


class RegisterRequest(BaseModel):
    """User registration request schema."""

    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")


class LoginResponse(BaseModel):
    """Login response schema."""

    access_token: str
    token_type: str = TokenType.BEARER.value


class RegisterResponse(BaseModel):
    """User registration response schema."""

    message: str
    username: str


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    status_code: int
