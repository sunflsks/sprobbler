import json
import os
import flask
from flask import g

from db import SpotifyConfig
from config import Config
from . import login
from flask_dance.contrib.spotify import spotify
from compiler.compiler_info import GlobalPlayInfo


def create_app() -> flask.Flask:
    app = flask.Flask(
        __name__, instance_relative_config=True, template_folder="./templates"
    )
    app.config.from_mapping(
        SECRET_KEY=Config().secret_key(), DATABASE=Config().database_location()
    )

    app.register_blueprint(login.bp, url_prefix="/login")

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
            "client_id": Config().spotify_info()[0],
            "client_secret": Config().spotify_info()[1],
        }

        new_token = spotify.refresh_token(spotify.auto_refresh_url, **extra)  # type: ignore
        SpotifyConfig.set_access_token(new_token)
        return "Refreshed token"

    @app.route("/data")
    def data():
        return json.dumps(GlobalPlayInfo.dict_representation())

    return app


if __name__ == "__main__":
    print(
        "running web server barebone, will not connect to backend db. should only be used for troubleshooting"
    )
    app = create_app()
    app.run()
