from __future__ import annotations

from datetime import date

from mongoengine import DateField, Document, FloatField, IntField, StringField


class Song(Document):
    """Song document model for MongoDB."""

    artist = StringField(required=True)
    title = StringField(required=True)
    difficulty = FloatField(required=True)
    level = IntField(required=True)
    released = DateField(required=True)

    meta = {
        "collection": "songs",
        "indexes": [
            "artist",
            "title",
            "level",
            {
                "fields": ["$artist", "$title"],
                "default_language": "english",
                "weights": {"artist": 10, "title": 10},
            },
        ],
    }


class Rating(Document):
    """Rating document model for MongoDB."""

    song_id = StringField(required=True)
    rating = IntField(required=True, min_value=1, max_value=5)

    meta = {"collection": "ratings", "indexes": ["song_id"]}


class RatingStats(Document):
    """Precomputed rating statistics per song for O(1) retrieval."""

    song_id = StringField(required=True, unique=True)
    count = IntField(default=0)
    sum = IntField(default=0)
    min = IntField(default=5)
    max = IntField(default=1)

    meta = {"collection": "rating_stats", "indexes": ["song_id"]}


