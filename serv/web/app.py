import flask
from .config import Config
from . import login
from flask_dance.contrib.spotify import spotify


def create_app() -> flask.Flask:
    app = flask.Flask(
        __name__, instance_relative_config=True, template_folder="./templates"
    )
    app.config.from_mapping(
        SECRET_KEY=Config.secret_key(), DATABASE=Config.database_location()
    )

    app.register_blueprint(login.bp, url_prefix="/login")

    @app.route("/")
    def root():
        if not spotify.authorized:
            print(flask.url_for("spotify.login"))
            return flask.render_template(
                "index.html",
                redirect_url=flask.url_for("spotify.login"),
            )
        resp = spotify.get("/v1/me")
        return flask.render_template(
            "logout.html",
            redirect_url="https://google.com",
            login_name=resp.json()["display_name"],
        )

    return app


if __name__ == "__main__":
    print(
        "running web server barebone, will not connect to backend db. should only be used for troubleshooting"
    )
    app = create_app()
    app.run()
