import os
import os
import tomllib
import pathlib
from enum import Enum

DEFAULT_CONFIG_PATH = pathlib.Path.home() / ".sprobblerconf.toml"


class Config:
    class Keys(Enum):
        CLIENT_ID = "client_id"
        CLIENT_SECRET = "client_secret"
        DATABASE_LOCATION = "db"
        DEVKEY = "devkey"
        CELERY_BROKER = "celery_broker"
        CELERY_BACKEND = "celery_backend"
        PORT = "port"
        SCROBBLE_INTERVAL = "scrobbling_interval"
        PSQL_DB = "psql_db"
        PSQL_USER = "psql_username"
        PSQL_PASS = "psql_password"

    @staticmethod
    def get(key: Keys) -> str | None:
        with open(DEFAULT_CONFIG_PATH, "rb") as f:
            try:
                return tomllib.load(f)["config"][key.value]
            except KeyError as err:
                print(err)
                return None

    @staticmethod
    def validate() -> bool:
        if not DEFAULT_CONFIG_PATH.exists():
            print(f"Config file not found at {DEFAULT_CONFIG_PATH}")
            return False

        for key in Config.Keys:
            if Config.get(key) is None:
                print(f"Missing key {key.value} in config file")
                return False

        return True

    @staticmethod
    def debug_enabled() -> bool:
        return os.environ.get("SPROBBLER_DEBUG") == "YES"
