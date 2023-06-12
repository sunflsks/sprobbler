import os
import sys

# make this actual config file later
# DEFAULT_CONFIG_PATH="config.toml"

DEFAULT_DB_PATH = "/tmp/sprobbler.sqlite"
CLIENT_ID = "49b4dbcee202434aba5f0bf89245dab2"
CLIENT_SECRET = "2d1aeebf903f4d48adc4b1fe44fb99f8"


class Config:
    @staticmethod
    def database_location() -> str:
        return DEFAULT_DB_PATH

    @staticmethod
    def secret_key() -> str:
        return "dev"

    @staticmethod
    def spotify_info() -> tuple:
        # (client_id, client_secret)
        return (CLIENT_ID, CLIENT_SECRET)
