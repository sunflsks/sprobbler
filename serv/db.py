from peewee import *
from web import config
from playhouse.sqlite_ext import *

database = SqliteDatabase(config.Config.database_location())


class BaseModel(Model):
    class Meta:
        database = database


class SpotifyConfig(BaseModel):
    access_token = JSONField()
    name = CharField()

    @staticmethod
    def get_access_token():
        with database:
            print(database)
            ret = None
            try:
                ret = SpotifyConfig.get(SpotifyConfig.name == "main")
            except Exception:
                pass
        return ret

    @staticmethod
    def set_access_token(token):
        with database:
            ret = SpotifyConfig.replace(name="main", access_token=token).execute()
        return ret

    @staticmethod
    def delete_access_token():
        with database:
            SpotifyConfig.delete().where(SpotifyConfig.name == "main").execute()


def init_db():
    print(f"Initializing database at {config.Config.database_location()}")
    with database:
        database.create_tables([SpotifyConfig])
