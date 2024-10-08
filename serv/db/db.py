from __future__ import annotations

import os
from utils.config import Config
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
import datetime
from .scrobble import Scrobble as ScrobbleRepresentation
from celery import shared_task, Task
from rnn.predict import predict_genres_for_song, load_model_and_mapping
import tempfile
import requests

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
                    fn.COUNT(Scrobble.played_at).alias("play_count"),
                    Album.id,
                )
                .join(Track, on=(Track.album == Album.id))
                .join(Scrobble, on=(Scrobble.track == Track.id))
                .group_by(Album.name, Album.cover_image_url, Album.id)
                .order_by(fn.COUNT(Scrobble.played_at).desc())
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
                    fn.COUNT(Scrobble.played_at).alias("play_count"),
                    Album.id,
                )
                .join(Track, on=(Track.album == Album.id))
                .join(Scrobble, on=(Scrobble.track == Track.id))
                .group_by(Album.name, Album.cover_image_url, Album.id)
                .where(Scrobble.played_at > (starting - timedelta))
                .order_by(fn.COUNT(Scrobble.played_at).desc())
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
                    fn.COUNT(Scrobble.played_at.distinct()).alias("play_count"),
                    Artist.id,
                )
                .join(ArtistTrack, on=(Artist.id == ArtistTrack.artist))
                .join(Scrobble, on=(Scrobble.track == ArtistTrack.track))
                .group_by(Artist.name, Artist.id)
                .order_by(fn.COUNT(Scrobble.played_at.distinct()).desc())
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
                    fn.COUNT(Scrobble.played_at.distinct()).alias("play_count"),
                    Artist.id,
                )
                .join(ArtistTrack, on=(Artist.id == ArtistTrack.artist))
                .join(Scrobble, on=(Scrobble.track == ArtistTrack.track))
                .where(Scrobble.played_at > (starting - timedelta))
                .group_by(Artist.name, Artist.id)
                .order_by(fn.COUNT(Scrobble.played_at.distinct()).desc())
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
                    fn.COUNT(Scrobble.played_at).alias("play_count"),
                    Track.id,
                )
                .join(Album, on=(Track.album == Album.id))
                .join(Scrobble, on=(Scrobble.track == Track.id))
                .group_by(Track.name, Album.cover_image_url, Track.id)
                .order_by(fn.COUNT(Scrobble.played_at).desc())
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
                    fn.COUNT(Scrobble.played_at).alias("play_count"),
                    Track.id,
                )
                .join(Album, on=(Track.album == Album.id))
                .join(Scrobble, on=(Scrobble.track == Track.id))
                .group_by(Track.name, Album.cover_image_url, Track.id)
                .where(Scrobble.played_at > (starting - timedelta))
                .order_by(fn.COUNT(Scrobble.played_at).desc())
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
    played_at = DateTimeField(primary_key=True)

    @staticmethod
    def play_count(track_id):
        return Scrobble.select().where(Scrobble.track == track_id).count()


class ExtendedHistory(BaseModel):
    """
    The point of this class is to archive the ENTIRE extended history imported by the user, in case
    they want to see/analyze it manually later (or in case we want to add more features to the app that require this data).
    """

    timestamp = DateTimeField(null=True)
    username = TextField(null=True)
    platform = TextField(null=True)
    ms_played = IntegerField(null=True)
    conn_country = TextField(null=True)
    ip_address = TextField(null=True)
    user_agent = TextField(null=True)
    track_name = TextField(null=True)
    artist_name = TextField(null=True)
    album_name = TextField(null=True)
    track_uri = TextField(null=True)
    episode_name = TextField(null=True)
    episode_show_name = TextField(null=True)
    episode_uri = TextField(null=True)
    reason_start = TextField(null=True)
    reason_end = TextField(null=True)
    shuffle = BooleanField(null=True)
    skipped = BooleanField(null=True)
    offline = BooleanField(null=True)
    offline_timestamp = DateTimeField(null=True)
    incognito_mode = BooleanField(null=True)


def init_db_if_not_exists() -> None:
    with database:
        if not database.table_exists("spotifyconfig"):
            # We don't initialize the extended_history table here, as we only generate it if extended data is imported manually by the user.
            print(f"DB not found, initializing as {dbname} with user {username}")
            database.create_tables(
                [SpotifyConfig, Album, Artist, Track, ArtistTrack, Scrobble]
            )


def insert_scrobble_into_db(
    scrobble: ScrobbleRepresentation, update_genre: bool = True
) -> bool:
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
            ).on_conflict_ignore().execute()

            if update_genre:
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
def update_predicted_genre_for_track(self, track_id) -> bool:
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

    else:
        return True
