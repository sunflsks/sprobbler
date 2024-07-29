from __future__ import annotations

from doctest import debug
from enum import unique
from os import name
from re import T
from config import Config
from utils.utils import debugprint
from peewee import (
    PostgresqlDatabase,
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
from playhouse.sqlite_ext import JSONField
from utils.scrobble import Scrobble as ScrobbleRepresentation

dbname = Config().get(Config.Keys.PSQL_DB)
username = Config().get(Config.Keys.PSQL_USER)
password = Config().get(Config.Keys.PSQL_PASS)

database = PostgresqlDatabase(dbname, user=username, password=password)


class BaseModel(Model):
    class Meta:
        database = database


class SpotifyConfig(BaseModel):
    access_token = JSONField()
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


class Artist(BaseModel):
    name = CharField()
    id = CharField(primary_key=True)


class Track(BaseModel):
    name = CharField()
    album = ForeignKeyField(Album, to_field="id")
    explicit = BooleanField()
    popularity = IntegerField()
    duration_ms = IntegerField()
    id = CharField(primary_key=True)


class ArtistTrack(BaseModel):
    artist = ForeignKeyField(Artist, to_field="id")
    track = ForeignKeyField(Track, to_field="id")

    class Meta:
        primary_key = False


class Scrobble(BaseModel):
    track = ForeignKeyField(Track, to_field="id")
    played_at = DateTimeField()
    id = IntegerField(primary_key=True)


class ten_most_played_tracks(BaseModel):
    name = CharField()
    play_count = IntegerField()
    cover_image_url = CharField()
    track_id = CharField(primary_key=True)


class ten_most_played_albums(BaseModel):
    name = CharField()
    play_count = IntegerField()
    cover_image_url = CharField()
    id = CharField(primary_key=True)


class ten_most_played_artists(BaseModel):
    name = CharField()
    play_count = IntegerField()
    id = CharField(primary_key=True)


class ten_most_recent_scrobbles(BaseModel):
    name = CharField()
    cover_image_url = CharField()
    played_at = DateTimeField()
    track_id = CharField(primary_key=True)


class scrobbles_by_timestamp(BaseModel):
    name = CharField(primary_key=True)
    cover_image_url = CharField()
    played_at = DateTimeField()
    track_id = CharField()


"""
def init_db_if_not_exists() -> None:
    with database:
        if not database.table_exists("spotifyconfig"):
            print(
                f"DB not found, initializing at {config.Config.get(config.Config.Keys.DATABASE_LOCATION)}"
            )
            database.create_tables(
                [SpotifyConfig, Album, Artist, Track, ArtistTrack, Scrobble]
            )
"""


def insert_scrobble_into_db(scrobble: ScrobbleRepresentation) -> bool:
    with database:
        try:
            # first insert the album into the database, if it does not already exist
            Album.insert(
                name=scrobble.track.album.name,
                album_type=scrobble.track.album.album_type,
                id=scrobble.track.album.id,
                cover_image_url=scrobble.track.album.cover_image_url,
            ).on_conflict_ignore().execute()

            # then insert the track into the database, if it does not already exist
            Track.insert(
                name=scrobble.track.name,
                album=scrobble.track.album.id,
                explicit=scrobble.track.explicit,
                popularity=scrobble.track.popularity,
                id=scrobble.track.id,
                duration_ms=scrobble.track.duration_ms,
            ).on_conflict_ignore().execute()

            # then insert the artists into the database, if they do not already exist, as well as set up artist-track relationships
            for artist in scrobble.track.artists:
                Artist.insert(
                    name=artist.name, id=artist.id
                ).on_conflict_ignore().execute()
                ArtistTrack.insert(
                    artist=artist.id, track=scrobble.track.id
                ).on_conflict_ignore().execute()

            # finally, insert the scrobble into the database
            Scrobble.insert(
                track=scrobble.track.id, played_at=scrobble.played_at
            ).execute()
            return True
        except PeeweeException as e:
            print(f"Could not load scrobble into database: {e}")
            return False
