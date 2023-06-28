from doctest import debug
import os
import time
import json
from urllib import response
from web.login import bp
from threading import Timer, Lock
from scrobbler.song import Song
from utils import debugprint

# how many seconds between each call to api
SCROBBLER_INTERVAL = 120
SPOTIFY_RECENTLY_PLAYED_URL = "/v1/me/player/recently-played"
SPOTIFY_RECENTLY_PLAYED_LIMIT = 50  # maximum value, who knows maybe the user is crazy

after = int(time.time())


# will cycle
def scrobble():
    params = {"limit": SPOTIFY_RECENTLY_PLAYED_LIMIT, "after": after}
    resp = bp.session.get(SPOTIFY_RECENTLY_PLAYED_URL, params=params)

    if resp.status_code != 200:
        debugprint(f"SCROBBLER: get was not successful: {resp}")
        return False

    try:
        response_dict = resp.json()
    except json.JSONDecodeError as err:
        debugprint(f"SCROBBLER: could not parse json: {err}")
        return False

    for entry in response_dict["items"]:
        song = Song(entry)
        print(f"Song {song.track} played at {song.played_at}")

    Timer(SCROBBLER_INTERVAL, scrobble).start()


def start_scrobbler():
    # check if auth token is available
    if not bp.session.authorized:
        debugprint(
            "SCROBBLER: session unauthorized, could not enable scrobbler, exiting"
        )
        return False

    debugprint("SCROBBLER: session authorized, enabling scrobbler")
    scrobble()
