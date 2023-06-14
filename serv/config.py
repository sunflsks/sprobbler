import os
import os
import sys
import tomllib
import pathlib

# make this actual config file later
# DEFAULT_CONFIG_PATH="config.toml"

DEFAULT_DB_PATH = "/tmp/sprobbler.sqlite"
CLIENT_ID = "49b4dbcee202434aba5f0bf89245dab2"
CLIENT_SECRET = "2d1aeebf903f4d48adc4b1fe44fb99f8"

DEFAULT_CONFIG_PATH = pathlib.Path.home() / ".sprobblerconf.toml"


class Config:
    def __init__(self):
        pathlib.Path(DEFAULT_CONFIG_PATH).touch()
        self.config_path = DEFAULT_CONFIG_PATH

    def __get_toml_dict(self):
        with open(self.config_path, "rb") as f:
            return tomllib.load(f)

    def database_location(self) -> str:
        confdict = self.__get_toml_dict()
        return confdict["config"]["db"]

    def secret_key(self) -> str:
        confdict = self.__get_toml_dict()
        return confdict["config"]["devkey"]

    def spotify_info(self) -> tuple:
        confdict = self.__get_toml_dict()
        client_id = confdict["config"]["client_id"]
        client_secret = confdict["config"]["client_secret"]
        return (client_id, client_secret)

    def validate_config(self):
        # we will just immediately skip to trying to read the config; if any exception is thrown, we'll catch it and return
        # it.
        try:
            confdict = self.__get_toml_dict()
            _ = self.database_location()
            _ = self.secret_key()
            _ = self.spotify_info()
            return True
        except Exception as ex:
            print(f"Could not load config: {repr(ex)}")
            return False

    def debug_enabled(self):
        return os.environ["SPROBBLER_DEBUG"] == "YES"
