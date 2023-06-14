from doctest import debug
import config
from utils import debugprint
from peewee import *
from playhouse.sqlite_ext import *

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
            except SpotifyConfig.DoesNotExist:
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


def init_db_if_not_exists():
    with database:
        if not database.table_exists("spotifyconfig"):
            print(
                f"DB not found, initializing at {config.Config().database_location()}"
            )
            database.create_tables([SpotifyConfig])
