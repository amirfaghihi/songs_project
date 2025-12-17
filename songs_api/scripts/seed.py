from __future__ import annotations

import json
from datetime import date

from songs_api.database import ensure_indexes
from songs_api.models.documents import Song


def seed_songs_from_file(file_path: str) -> None:
    """Seed songs from a JSON file into MongoDB if the collection is empty."""
    ensure_indexes()

    existing_count = Song.objects.count()
    if existing_count > 0:
        print(f"Songs collection already has {existing_count} documents. Skipping seed.")
        return

    with open(file_path, encoding="utf-8") as f:
        songs_data = [json.loads(line) for line in f if line.strip()]

    songs = []
    for data in songs_data:
        released_str = data.get("released", "")
        released_date = date.fromisoformat(released_str) if released_str else date.today()

        song = Song(
            artist=data["artist"],
            title=data["title"],
            difficulty=float(data["difficulty"]),
            level=int(data["level"]),
            released=released_date,
        )
        songs.append(song)

    if songs:
        Song.objects.insert(songs)
        print(f"Seeded {len(songs)} songs into the database.")
    else:
        print("No songs to seed.")
