import json
import requests
from flask import Blueprint
from flask_dance.contrib.spotify import spotify  # type: ignore

# since we use the json returned by spotify directly on the client, we can just have one wrapper
# function for all the info endpoints, and just return the json directly from the spotify API

info_bp = Blueprint("info", __name__)
err_string = "ERROR: Could not complete request"


def get_value_from_spotify(url: str) -> tuple | dict:
    try:
        resp = spotify.get(url)
    except requests.exceptions.RequestException as e:
        print(f"{err_string}: {e}")
        return err_string, 502

    if resp.status_code != 200:
        print(f"{err_string}: {resp}")
        return err_string, 502

    try:
        return resp.json()
    except json.JSONDecodeError as e:
        print(f"{err_string}: {e}")
        return {}


@info_bp.route("/")
def root():
    return "available options are album, track, artist"


@info_bp.route("/track/<string:track_id>")
def track(track_id):
    return get_value_from_spotify(f"/v1/tracks/{track_id}")


@info_bp.route("/album/<string:album_id>")
def album(album_id):
    return get_value_from_spotify(f"/v1/albums/{album_id}")


@info_bp.route("/artist/<string:artist_id>")
def artist(artist_id):
    return get_value_from_spotify(f"/v1/artists/{artist_id}")
