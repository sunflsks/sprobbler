import os, json

from db import SpotifyConfig
from config import Config
from flask import Flask, redirect, url_for

from flask_dance.consumer.storage.sqla import BaseStorage
from flask_dance.contrib.spotify import make_spotify_blueprint, spotify

client_id, secret = Config().spotify_info()

SCOPES = ["user-read-recently-played", "user-top-read"]


class PeeWeeSQLStorage(BaseStorage):
    def get(self, blueprint):
        config = SpotifyConfig.get_access_token()
        if not config:
            return None
        return config.access_token

    def set(self, blueprint, token):
        return SpotifyConfig.set_access_token(token)

    def delete(self, blueprint):
        SpotifyConfig.delete_access_token()


bp = make_spotify_blueprint(
    client_id=client_id,
    client_secret=secret,
    storage=PeeWeeSQLStorage(),
    scope=SCOPES,
)
