import json
import flask
from flask import g
from peewee import PeeweeException
import decimal

from celery import Celery, Task
from db import SpotifyConfig, init_db_if_not_exists, genre_stats
from config import Config
from web.blueprints import login, info, reports
from flask_dance.contrib.spotify import spotify  # type: ignore
from play_info.utils import PlayedItemsJSONProvider
from play_info.track import (
    scrobbles_paginated as scrobbles_paginated_internal,
    track_scrobble_info,
    ten_most_recent_scrobbles,
)
from scrobbler import scrobbler  # this is needed for celery-beat! don't delete
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
            task_routes={
                "db.update_predicted_genre_for_track": {"queue": "rnn_queue"},
                "scrobbler.scrobbler.start_scrobbler": {"queue": "scrobbler_queue"},
            },
        ),
    )

    init_db_if_not_exists()

    celery_init(app)

    app.json = PlayedItemsJSONProvider(app)
    app.register_blueprint(login.bp, url_prefix="/login")
    app.register_blueprint(info.bp, url_prefix="/info")
    app.register_blueprint(reports.bp, url_prefix="/reports")

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
            output["ten_most_recent_scrobbles"] = ten_most_recent_scrobbles()
            output["scrobble_count"] = track_info.scrobble_count
            output["track_count"] = track_info.track_count
            output["listening_time"] = track_info.listening_time

            return flask.jsonify(output)
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
            return flask.jsonify(scrobbles_paginated_internal(start_timestamp, count))
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
