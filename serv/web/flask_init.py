import flask
from config import Config

def instantiate_web_server() -> flask.Flask:
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=Config.secret_key(),
        DATABASE=Config.database_location()
    )

    @app.route("/")
    def root():
        return "root"

    return app
