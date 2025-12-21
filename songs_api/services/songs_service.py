from __future__ import annotations

from songs_api.infrastructure import UnitOfWork
from songs_api.models.documents import Song
from songs_api.schemas import AverageDifficultyResponse, SearchSongsResponse, SongResponse, SongsListResponse


class SongsService:
    def list_songs(self, page: int, page_size: int) -> SongsListResponse:
        skip = (page - 1) * page_size

        with UnitOfWork() as uow:
            songs, total = uow.songs_repository.list_songs(skip=skip, limit=page_size)

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
        skip = (page - 1) * page_size

        with UnitOfWork() as uow:
            songs, total = uow.songs_repository.search_songs(query=message, skip=skip, limit=page_size)

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
        with UnitOfWork() as uow:
            avg = uow.songs_repository.get_average_difficulty(level=level)

        return AverageDifficultyResponse(average_difficulty=avg, level=level)

    @staticmethod
    def _song_to_response(song: Song) -> SongResponse:
        return SongResponse(
            id=str(song.id),
            artist=song.artist,
            title=song.title,
            difficulty=song.difficulty,
            level=song.level,
            released=song.released,
        )
