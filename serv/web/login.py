import os, json
from .config import Config
from flask import Flask, redirect, url_for

# from flask_sqlalchemy import SQLAlchemy
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage, BaseStorage
from flask_dance.contrib.spotify import make_spotify_blueprint, spotify

client_id, secret = Config.spotify_info()
print(f"CLID: {client_id}, SEC: {secret}")


class FileStorage(BaseStorage):
    def __init__(self, filepath):
        super(FileStorage, self).__init__()
        self.filepath = filepath

    def get(self, blueprint):
        if not os.path.exists(self.filepath):
            return None
        with open(self.filepath) as f:
            return json.load(f)

    def set(self, blueprint, token):
        with open(self.filepath, "w") as f:
            json.dump(token, f)

    def delete(self, blueprint):
        os.remove(self.filepath)


bp = make_spotify_blueprint(
    client_id=client_id, client_secret=secret, storage=FileStorage("/tmp/token.json")
)
