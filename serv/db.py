from doctest import debug
from os import name
import config
from utils.utils import debugprint
from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    ForeignKeyField,
    BooleanField,
    IntegerField,
    DateTimeField,
    Model,
    DoesNotExist,
)
from playhouse.sqlite_ext import JSONField
from utils.song import Song

database = SqliteDatabase(config.Config().database_location())


class BaseModel(Model):
    class Meta:
        database = database


class SpotifyConfig(BaseModel):
    access_token = JSONField()
    name = CharField()

    @staticmethod
    def get_access_token():
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
    def set_access_token(token):
        with database:
            debugprint("setting access token")
            ret = SpotifyConfig.replace(name="main", access_token=token).execute()
        return ret

    @staticmethod
    def delete_access_token():
        with database:
            debugprint("deleting access token")
            SpotifyConfig.delete().where(SpotifyConfig.name == "main").execute()


class Album(BaseModel):
    name = CharField()
    album_type = CharField()
    id = CharField(primary_key=True)


class Artist(BaseModel):
    name = CharField()
    id = CharField(primary_key=True)


class Track(BaseModel):
    name = CharField()
    album = ForeignKeyField(Album, to_field="id")
    explicit = BooleanField()
    popularity = IntegerField()
    id = CharField(primary_key=True)


class ArtistTrack(BaseModel):
    artist = ForeignKeyField(Artist, to_field="id")
    track = ForeignKeyField(Track, to_field="id")


class Scrobble(BaseModel):
    track = ForeignKeyField(Track, to_field="id")
    played_at = DateTimeField()


def init_db_if_not_exists():
    with database:
        if not database.table_exists("spotifyconfig"):
            print(
                f"DB not found, initializing at {config.Config().database_location()}"
            )
            database.create_tables(
                [SpotifyConfig, Album, Artist, Track, ArtistTrack, Scrobble]
            )
