from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class SongResponse(BaseModel):
    """Song response schema."""

    id: str
    artist: str
    title: str
    difficulty: float
    level: int
    released: date


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int
    page_size: int
    total: int
    total_pages: int


class PaginationQueryParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class SearchQueryParams(BaseModel):
    """Query parameters for search."""

    message: str = Field(..., min_length=1, description="Search query")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


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


class AddRatingRequest(BaseModel):
    """Request to add a rating."""

    song_id: str
    rating: int = Field(ge=1, le=5)


class RatingStatsResponse(BaseModel):
    """Response for rating statistics."""

    song_id: str
    average: float | None
    lowest: int | None
    highest: int | None
    count: int


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response schema."""

    access_token: str
    token_type: str = "bearer"


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    status_code: int
