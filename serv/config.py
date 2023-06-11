import os
import sys

# make this actual config file later
#DEFAULT_CONFIG_PATH="config.toml"

DEFAULT_DB_PATH="/tmp/sprobbler.sqlite"

class Config:
    @staticmethod
    def database_location() -> str:
        return DEFAULT_DB_PATH

    @staticmethod
    def secret_key() -> str:
        return "dev"