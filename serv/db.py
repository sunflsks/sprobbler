from __future__ import annotations

import os
import sys
from re import T
from config import Config
from utils.utils import debugprint
from peewee import (
    Model,
    CharField,
    ForeignKeyField,
    BooleanField,
    IntegerField,
    DateTimeField,
    Model,
    DoesNotExist,
    PeeweeException,
)
from playhouse.postgres_ext import *
from utils.scrobble import Scrobble as ScrobbleRepresentation
import requests
import os
import tempfile
from celery import shared_task, Task
from rnn.predict import predict_genres_for_song, load_model_and_mapping
from peewee import PeeweeException
import datetime

sys.path.append(os.getcwd())

dbname = Config.get(Config.Keys.PSQL_DB)
username = Config.get(Config.Keys.PSQL_USER)
password = Config.get(Config.Keys.PSQL_PASS)

database = PostgresqlExtDatabase(dbname, user=username, password=password)


class BaseModel(Model):
    class Meta:
        database = database


class SpotifyConfig(BaseModel):
    access_token = BinaryJSONField()
    name = CharField(unique=True)

    @staticmethod
    def get_access_token() -> SpotifyConfig | None:
        ret = None
        with database:
            debugprint("opening database to retrieve token")
            try:
                ret = SpotifyConfig.get(SpotifyConfig.name == "main")
                debugprint("token was found, returning")
            except DoesNotExist:
                debugprint("token not found, returning None")
                pass
        return ret

    @staticmethod
    def set_access_token(token) -> None:
        token = dict(token)
        print(token)
        with database:
            debugprint("setting access token")
            ret = (
                SpotifyConfig.insert(name="main", access_token=token)
                .on_conflict(
                    conflict_target=[SpotifyConfig.name],
                    preserve=[SpotifyConfig.access_token],
                )
                .execute()
            )
        return ret

    @staticmethod
    def delete_access_token() -> None:
        with database:
            debugprint("deleting access token")
            SpotifyConfig.delete().where(SpotifyConfig.name == "main").execute()


class Album(BaseModel):
    name = CharField()
    album_type = CharField()
    id = CharField(primary_key=True)
    cover_image_url = CharField(null=True)

    @staticmethod
    def ten_most_played_albums():
        with database:
            return (
                Album.select(
                    Album.name,
                    Album.cover_image_url,
                    fn.COUNT(Scrobble.id).alias("play_count"),
                    Album.id,
                )
                .join(Track, on=(Track.album == Album.id))
                .join(Scrobble, on=(Scrobble.track == Track.id))
                .group_by(Album.name, Album.cover_image_url, Album.id)
                .order_by(fn.COUNT(Scrobble.id).desc())
                .limit(10)
            )

    @staticmethod
    def ten_most_played_albums_timedelta(
        starting=datetime.datetime.now(), timedelta=datetime.timedelta(days=30)
    ):
        with database:
            return (
                Album.select(
                    Album.name,
                    Album.cover_image_url,
                    fn.COUNT(Scrobble.id).alias("play_count"),
                    Album.id,
                )
                .join(Track, on=(Track.album == Album.id))
                .join(Scrobble, on=(Scrobble.track == Track.id))
                .group_by(Album.name, Album.cover_image_url, Album.id)
                .where(Scrobble.played_at > (starting - timedelta))
                .order_by(fn.COUNT(Scrobble.id).desc())
                .limit(10)
            )


class Artist(BaseModel):
    name = CharField()
    id = CharField(primary_key=True)

    @staticmethod
    def ten_most_played_artists():
        with database:
            return (
                Artist.select(
                    Artist.name,
                    fn.COUNT(Scrobble.id.distinct()).alias("play_count"),
                    Artist.id,
                )
                .join(ArtistTrack, on=(Artist.id == ArtistTrack.artist))
                .join(Scrobble, on=(Scrobble.track == ArtistTrack.track))
                .group_by(Artist.name, Artist.id)
                .order_by(fn.COUNT(Scrobble.id.distinct()).desc())
                .limit(10)
            )

    @staticmethod
    def ten_most_played_artists_timedelta(
        starting=datetime.datetime.now(), timedelta=datetime.timedelta(days=30)
    ):
        with database:
            return (
                Artist.select(
                    Artist.name,
                    fn.COUNT(Scrobble.id.distinct()).alias("play_count"),
                    Artist.id,
                )
                .join(ArtistTrack, on=(Artist.id == ArtistTrack.artist))
                .join(Scrobble, on=(Scrobble.track == ArtistTrack.track))
                .where(Scrobble.played_at > (starting - timedelta))
                .group_by(Artist.name, Artist.id)
                .order_by(fn.COUNT(Scrobble.id.distinct()).desc())
                .limit(10)
            )


class Track(BaseModel):
    name = CharField()
    album = ForeignKeyField(Album, to_field="id")
    explicit = BooleanField()
    popularity = IntegerField()
    duration_ms = IntegerField()
    id = CharField(primary_key=True)
    predicted_genre = BinaryJSONField(null=True)

    @staticmethod
    def scrobbles_by_timestamp():
        with database:
            return (
                Track.select(
                    Track.name, Album.cover_image_url, Scrobble.played_at, Track.id
                )
                .join(Album, on=(Scrobble.track == Album.id))
                .join(Scrobble, on=(Scrobble.track == Track.id))
                .order_by(Scrobble.played_at.desc())
            )

    @staticmethod
    def scrobbles_paginated(start, count):
        with database:
            return (
                Track.select(
                    Track.name, Album.cover_image_url, Scrobble.played_at, Track.id
                )
                .join(Scrobble, on=(Scrobble.track == Track.id))
                .join(Album, on=(Track.album == Album.id))
                .order_by(Scrobble.played_at.desc())
                .where(
                    Scrobble.played_at <= start,
                )
                .limit(count)
            )

    @staticmethod
    def ten_most_recent_scrobbles():
        with database:
            return (
                Track.select(
                    Track.name, Album.cover_image_url, Scrobble.played_at, Track.id
                )
                .join(Album, on=(Track.album == Album.id))
                .join(Scrobble, on=(Scrobble.track == Track.id))
                .order_by(Scrobble.played_at.desc())
                .limit(10)
            )

    @staticmethod
    def ten_most_played_tracks():
        with database:
            return (
                Track.select(
                    Track.name,
                    Album.cover_image_url,
                    fn.COUNT(Scrobble.id).alias("play_count"),
                    Track.id,
                )
                .join(Album, on=(Track.album == Album.id))
                .join(Scrobble, on=(Scrobble.track == Track.id))
                .group_by(Track.name, Album.cover_image_url, Track.id)
                .order_by(fn.COUNT(Scrobble.id).desc())
                .limit(10)
            )

    @staticmethod
    def ten_most_played_tracks_timedelta(
        starting=datetime.datetime.now(), timedelta=datetime.timedelta(days=30)
    ):
        with database:
            return (
                Track.select(
                    Track.name,
                    Album.cover_image_url,
                    fn.COUNT(Scrobble.id).alias("play_count"),
                    Track.id,
                )
                .join(Album, on=(Track.album == Album.id))
                .join(Scrobble, on=(Scrobble.track == Track.id))
                .group_by(Track.name, Album.cover_image_url, Track.id)
                .where(Scrobble.played_at > (starting - timedelta))
                .order_by(fn.COUNT(Scrobble.id).desc())
                .limit(10)
            )

    @staticmethod
    def set_predicted_genre(track_id, genre):
        with database:
            try:
                Track.update(predicted_genre=genre).where(
                    Track.id == track_id
                ).execute()
                return True

            except PeeweeException as e:
                print(f"Could not update predicted genre for track: {e}")
                return False

    @staticmethod
    def get_predicted_genre(track_id):
        with database:
            return Track.get(Track.id == track_id).predicted_genre


class ArtistTrack(BaseModel):
    artist = ForeignKeyField(Artist, to_field="id")
    track = ForeignKeyField(Track, to_field="id")

    class Meta:
        primary_key = False


class Scrobble(BaseModel):
    track = ForeignKeyField(Track, to_field="id")
    played_at = DateTimeField()
    id = IntegerField(primary_key=True)


def highest_day_stats(starting, timedelta):
    with database:
        highest_day_stats = (
            Scrobble.select(
                fn.COUNT(Scrobble.id).alias("play_count"),
                fn.DATE_TRUNC("day", Scrobble.played_at).alias("day"),
            )
            .group_by(fn.DATE_TRUNC("day", Scrobble.played_at))
            .order_by(fn.COUNT(Scrobble.id).desc())
            .where(Scrobble.played_at > (starting - timedelta))
            .first()
        )

    return {
        "date": highest_day_stats.day,
        "play_count": highest_day_stats.play_count,
    }


def average_play_stats(start, timedelta):
    interval = None

    match timedelta.days:
        case 7:
            interval = 7
        case 30:
            interval = 6
        case 365:
            interval = 12
        case _:
            interval = 6

    with database:
        new_timedelta = timedelta / interval
        avg = []
        for i in range(0, interval):
            end = start - new_timedelta

            avg.append(
                {
                    "count": round(
                        (
                            Scrobble.select(fn.COUNT(Scrobble.id).alias("play_count"))
                            .where(Scrobble.played_at.between(end, start))
                            .scalar()
                        )
                        / new_timedelta.days
                    ),
                    "start": end,  # Switch these two, as it flows better chronologically (start -> end, start is earlier than end)
                    "end": start,
                }
            )
            start = end
        return avg


def stats_for_timedelta(
    starting=datetime.datetime.now(), timedelta=datetime.timedelta(days=30)
):
    if timedelta is None:
        # seconds since epoch
        timedelta = datetime.timedelta(seconds=datetime.datetime.now().timestamp())

    with database:
        stats = {
            "avg_scrobbles_per_day": round(
                Scrobble.select()
                .where(Scrobble.played_at > (starting - timedelta))
                .count()
                / timedelta.days,
            ),
            "listening_time_ms": Scrobble.select(fn.SUM(Track.duration_ms))
            .join(Track)
            .where(Scrobble.played_at > (starting - timedelta))
            .scalar(),
            "num_artists": Scrobble.select(
                fn.COUNT(fn.DISTINCT(Artist.id)).alias("count")
            )
            .where(Scrobble.played_at > (starting - timedelta))
            .join(Track)
            .join(ArtistTrack)
            .join(Artist)
            .get()
            .count,
            "num_albums": Scrobble.select(
                fn.COUNT(fn.DISTINCT(Album.id)).alias("count")
            )
            .where(Scrobble.played_at > (starting - timedelta))
            .join(Track, on=(Scrobble.track == Track.id))
            .join(Album, on=(Track.album == Album.id))
            .get()
            .count,
            "num_tracks": Scrobble.select(
                fn.COUNT(fn.DISTINCT(Track.id)).alias("count")
            )
            .join(Track)
            .where(Scrobble.played_at > (starting - timedelta))
            .get()
            .count,
            "highest_day": highest_day_stats(starting, timedelta),
            "averages": average_play_stats(starting, timedelta),
        }

        return stats


def init_db_if_not_exists() -> None:
    with database:
        if not database.table_exists("spotifyconfig"):
            print(f"DB not found, initializing as {dbname} with user {username}")
            database.create_tables(
                [SpotifyConfig, Album, Artist, Track, ArtistTrack, Scrobble]
            )


def insert_scrobble_into_db(scrobble: ScrobbleRepresentation) -> bool:
    with database:
        try:
            Album.insert(
                name=scrobble.track.album.name,
                album_type=scrobble.track.album.album_type,
                id=scrobble.track.album.id,
                cover_image_url=scrobble.track.album.cover_image_url,
            ).on_conflict_ignore().execute()

            Track.insert(
                name=scrobble.track.name,
                album=scrobble.track.album.id,
                explicit=scrobble.track.explicit,
                popularity=scrobble.track.popularity,
                id=scrobble.track.id,
                duration_ms=scrobble.track.duration_ms,
            ).on_conflict_ignore().execute()

            for artist in scrobble.track.artists:
                Artist.insert(
                    name=artist.name, id=artist.id
                ).on_conflict_ignore().execute()
                ArtistTrack.insert(
                    artist=artist.id, track=scrobble.track.id
                ).on_conflict_ignore().execute()

            Scrobble.insert(
                track=scrobble.track.id, played_at=scrobble.played_at
            ).execute()

            update_predicted_genre_for_track.delay(scrobble.track.id)

            return True
        except PeeweeException as e:
            print(f"Could not load scrobble into database: {e}")
            return False


class RNNTask(Task):
    _mappings = None

    @property
    def model_and_mapping(self):
        if self._mappings == None:
            self._mappings = load_model_and_mapping()
        return self._mappings


@shared_task(ignore_result=True, bind=True, base=RNNTask)
def update_predicted_genre_for_track(self, track_id):

    model, mapping = self.model_and_mapping

    if Track.get_predicted_genre(track_id) is None:
        track_info = requests.get(
            f"http://localhost:{Config.get(Config.Keys.PORT)}/info/track/{track_id}"
        )

        preview_url = track_info.json()["preview_url"]

        with tempfile.TemporaryDirectory() as tempdir:
            file_path = os.path.join(tempdir, "sample.mp3")

            with open(file_path, "wb") as f:
                f.write(requests.get(preview_url).content)

            genres = predict_genres_for_song(file_path, model, mapping)

        with database:
            try:
                Track.update(predicted_genre=genres).where(
                    Track.id == track_id
                ).execute()
                return True
            except PeeweeException as e:
                print(f"Could not update predicted genre for track: {e}")
                return False
