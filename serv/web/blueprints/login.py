import os, json

from db.db import SpotifyConfig
from utils.config import Config

from flask_dance.consumer.storage.sqla import BaseStorage  # type: ignore
from flask_dance.contrib.spotify import make_spotify_blueprint, spotify  # type: ignore

client_id = Config.get(Config.Keys.CLIENT_ID)
secret = Config.get(Config.Keys.CLIENT_SECRET)

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

# un workaround para asegurarse de que el token se refresca cuando sea necesario, lo ideal seria
# que make_spotify_blueprint lo haga automaticamente pero no lo hace :(((
bp.auto_refresh_url = "https://accounts.spotify.com/api/token"
bp.auto_refresh_kwargs = {
    "client_id": client_id,
    "client_secret": secret,
}
