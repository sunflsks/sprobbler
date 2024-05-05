import json
import os
import flask
from flask import g
import celery
import decimal

from celery import Celery, Task
from db import SpotifyConfig
from config import Config
from . import login
from flask_dance.contrib.spotify import spotify  # type: ignore
from play_info.global_play_info import GlobalPlayInfo
from scrobbler import scrobbler  # this is needed for celery-beat! don't delete
from web.blueprints.info import info_bp
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
        return json.dumps(
            GlobalPlayInfo().dict_representation(), default=json_type_handler
        )

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
