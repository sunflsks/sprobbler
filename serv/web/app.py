import json
import os
import flask
from flask import g
from peewee import PeeweeException
import celery
import decimal

from celery import Celery, Task
from db import SpotifyConfig
from config import Config
from . import login
from flask_dance.contrib.spotify import spotify  # type: ignore
from play_info.utils import PlayedItemsJSONEncoder
from play_info.albums import ten_most_played_albums
from play_info.artists import ten_most_played_artists
from play_info.track import (
    ten_most_played_tracks,
    scrobbles_paginated as scrobbles_paginated_internal,
    scrobbles_between_timestamps,
    track_scrobble_info,
    ten_most_recent_scrobbles,
)
from scrobbler import scrobbler  # this is needed for celery-beat! don't delete
from web.blueprints.info import info_bp, track
import datetime


def json_type_handler(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return int(obj)
    raise TypeError("unknown")


def create_app() -> flask.Flask:
    app = flask.Flask(
        __name__, instance_relative_config=True, template_folder="./templates"
    )
    app.config.from_mapping(
        SECRET_KEY=Config.get(Config.Keys.CLIENT_SECRET),
        DATABASE=Config.get(Config.Keys.DATABASE_LOCATION),
        CELERY=dict(
            broker_url=Config.get(Config.Keys.CELERY_BROKER),
            result_backend=Config.get(Config.Keys.CELERY_BACKEND),
            task_ignore_result=True,
            beat_schedule={
                "update-play-info": {
                    "task": "scrobbler.scrobbler.start_scrobbler",
                    "schedule": Config.get(Config.Keys.SCROBBLE_INTERVAL) or 60,
                }
            },
        ),
    )

    celery_init(app)

    app.register_blueprint(login.bp, url_prefix="/login")
    app.register_blueprint(info_bp, url_prefix="/info")

    @app.route("/")
    def root():
        if not spotify.authorized:  # type: ignore
            return flask.render_template(
                "login.html",
                redirect_url=flask.url_for("spotify.login"),
            )
        resp = spotify.get("/v1/me")  # type: ignore
        assert resp.ok
        return flask.render_template(
            "logout.html",
            redirect_url=flask.url_for("logout"),
            login_name=resp.json()["display_name"],
        )

    # it doesn't look like spotify has an API to revoke tokens, so we'll just delete it here and
    # wait for it to expire on their end (they have a pretty short lifetime, this *should* be fine)
    @app.route("/logout")
    def logout():
        if not spotify.authorized:  # type: ignore
            return flask.redirect(flask.url_for("root"))
        SpotifyConfig.delete_access_token()
        return "Logged out"

    @app.route("/refresh")
    def refresh():
        if not spotify.authorized:  # type: ignore
            return flask.redirect(flask.url_for("root"))

        extra = {
            "client_id": Config.get(Config.Keys.CLIENT_ID),
            "client_secret": Config.get(Config.Keys.CLIENT_SECRET),
        }

        new_token = spotify.refresh_token(spotify.auto_refresh_url, **extra)  # type: ignore
        SpotifyConfig.set_access_token(new_token)
        return "Refreshed token"

    @app.route("/global")
    def data():
        track_info = track_scrobble_info()
        output = {}
        try:
            output["ten_most_played_artists"] = ten_most_played_artists()
            output["ten_most_played_albums"] = ten_most_played_albums()
            output["ten_most_played_tracks"] = ten_most_played_tracks()
            output["ten_most_recent_scrobbles"] = ten_most_recent_scrobbles()
            output["scrobble_count"] = track_info.scrobble_count
            output["track_count"] = track_info.track_count
            output["listening_time"] = track_info.listening_time

            return json.dumps(output, cls=PlayedItemsJSONEncoder)
        except (TypeError, PeeweeException) as e:
            return f"Error: {e}"

    @app.route("/scrobbles_between")
    def scrobbles_between():
        start = flask.request.args.get("start")
        end = flask.request.args.get("end")

        if start is None or end is None:
            return "Invalid timestamp"

        try:
            start_timestamp = datetime.datetime.fromtimestamp(int(start))
            end_timestamp = datetime.datetime.fromtimestamp(int(end))
        except (ValueError, OverflowError) as e:
            return f"Invalid timestamp: {e}"

        try:
            return json.dumps(
                scrobbles_between_timestamps(start_timestamp, end_timestamp),
                cls=PlayedItemsJSONEncoder,
            )
        except (TypeError, PeeweeException) as e:
            return f"Error: {e}"

    @app.route("/scrobbles_paginated")
    def scrobbles_paginated():
        start = flask.request.args.get("from")
        count = flask.request.args.get("count")

        if start is None or count is None:
            return "Invalid timestamp/count value"

        try:
            start_timestamp = datetime.datetime.fromtimestamp(int(start))
            count = int(count)
        except (ValueError, OverflowError) as e:
            return f"Invalid timestamp/count value: {e}"

        try:
            return json.dumps(
                scrobbles_paginated_internal(start_timestamp, count),
                cls=PlayedItemsJSONEncoder,
            )
        except (TypeError, PeeweeException) as e:
            return f"Error: {e}"

    return app


def celery_init(app: flask.Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app

    return celery_app
