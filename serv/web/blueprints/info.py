import datetime
import db.db as db
import json
import requests
from flask import Blueprint
from peewee import PeeweeException
from flask_dance.contrib.spotify import spotify  # type: ignore

# since we use the json returned by spotify directly on the client, we can just have one wrapper
# function for all the info endpoints, and just return the json directly from the spotify API

bp = Blueprint("info", __name__)
err_string = "ERROR: Could not complete request"


def get_value_from_spotify(url: str) -> tuple | dict:
    if datetime.datetime.now() < get_value_from_spotify.retry_after:
        print(f"Rate limited, retry after: {get_value_from_spotify.retry_after}")
        return f"Rate limited, retry after: {get_value_from_spotify.retry_after}", 429

    try:
        resp = spotify.get(url)
    except requests.exceptions.RequestException as e:
        print(f"{err_string}: {e}")
        return f"{err_string}: {e}", 502

    if resp.status_code != 200:
        if resp.status_code == 429:
            get_value_from_spotify.retry_after = (
                datetime.datetime.now()
                + datetime.timedelta(seconds=int(resp.headers["Retry-After"]))
            )
            print(f"Rate limited, retry after: {get_value_from_spotify.retry_after}")
        print(f"{err_string}: {resp}")
        return f"{err_string}: {resp}", 502

    try:
        return resp.json()
    except json.JSONDecodeError as e:
        print(f"{err_string}: {e}")
        return {}


get_value_from_spotify.retry_after = datetime.datetime.now()


@bp.route("/")
def root():
    return "available options are album, track, artist"


@bp.route("/track/<string:track_id>")
def track(track_id):
    with db.database:
        try:
            predicted_genres = db.Track.get(
                db.Track.id == track_id.strip()
            ).predicted_genre
        except db.DoesNotExist:
            predicted_genres = None

    response = get_value_from_spotify(f"/v1/tracks/{track_id}")
    if not isinstance(response, dict):
        return response

    # Inject predicted genre and play count from DB
    response["predicted_genres"] = (
        predicted_genres if predicted_genres is not None else []
    )

    response["play_count"] = db.Scrobble.play_count(track_id.strip())

    return response


@bp.route("/album/<string:album_id>")
def album(album_id):
    return get_value_from_spotify(f"/v1/albums/{album_id}")


@bp.route("/artist/<string:artist_id>")
def artist(artist_id):
    return get_value_from_spotify(f"/v1/artists/{artist_id}")
