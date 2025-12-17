from __future__ import annotations

from songs_api.models.documents import Song
from songs_api.schemas import AverageDifficultyResponse, SongResponse, SongsListResponse, SearchSongsResponse
from songs_api.uow import UnitOfWork


class SongsService:
    """Service layer for songs-related business logic."""

    def list_songs(self, page: int, page_size: int) -> SongsListResponse:
        """
        Get paginated list of songs.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            SongsListResponse with data and pagination metadata
        """
        skip = (page - 1) * page_size
        
        with UnitOfWork() as uow:
            songs, total = uow.list_songs(skip=skip, limit=page_size)

        data = [self._song_to_response(song) for song in songs]
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return SongsListResponse(
            data=data,
            pagination={
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
            },
        )

    def search_songs(self, message: str, page: int, page_size: int) -> SearchSongsResponse:
        """
        Search songs by artist or title.
        
        Args:
            message: Search query string
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            SearchSongsResponse with matching songs and pagination
        """
        skip = (page - 1) * page_size
        
        with UnitOfWork() as uow:
            songs, total = uow.search_songs(query=message, skip=skip, limit=page_size)

        data = [self._song_to_response(song) for song in songs]
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        return SearchSongsResponse(
            message=message,
            data=data,
            pagination={
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
            },
        )

    def get_average_difficulty(self, level: int | None = None) -> AverageDifficultyResponse:
        """
        Calculate average difficulty of songs, optionally filtered by level.
        
        Args:
            level: Optional level filter
            
        Returns:
            AverageDifficultyResponse with calculated average
        """
        with UnitOfWork() as uow:
            avg = uow.get_average_difficulty(level=level)

        return AverageDifficultyResponse(average_difficulty=avg, level=level)

    @staticmethod
    def _song_to_response(song: Song) -> SongResponse:
        """Convert Song document to SongResponse schema."""
        return SongResponse(
            id=str(song.id),
            artist=song.artist,
            title=song.title,
            difficulty=song.difficulty,
            level=song.level,
            released=song.released,
        )



