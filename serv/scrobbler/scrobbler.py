from doctest import debug
import os
import time
import json
from urllib import response

import requests
from web.login import bp
from threading import Timer, Lock
from utils.scrobble import Scrobble
from utils.utils import debugprint, repeat
from db import insert_scrobble_into_db

# it seems a song is only registered when fully, 100 percent played; partial plays do not count
# as a recently played song. however, if fast forwarded to the end it DOES count.

# how many seconds between each call to api
SCROBBLER_INTERVAL = 120
SPOTIFY_RECENTLY_PLAYED_URL = "/v1/me/player/recently-played"
SPOTIFY_RECENTLY_PLAYED_LIMIT = 50  # maximum value, who knows maybe the user is crazy

after = time.time_ns() // 1000000  # convert to ms


# will cycle
@repeat(SCROBBLER_INTERVAL)
def scrobble() -> bool:
    global after

    print(f"SCROBBLER: starting @ {after}")

    params = {"limit": SPOTIFY_RECENTLY_PLAYED_LIMIT, "after": after}
    try:
        resp = bp.session.get(SPOTIFY_RECENTLY_PLAYED_URL, params=params)
    except requests.exceptions.RequestException as err:
        print(f"ERROR: Could not get recently played songs: {err}")
        return False

    if resp.status_code != 200:
        debugprint(f"SCROBBLER: get was not successful: {resp}")
        return False

    try:
        response_dict = resp.json()
    except json.JSONDecodeError as err:
        debugprint(f"SCROBBLER: could not parse json: {err}")
        return False

    for entry in response_dict["items"]:
        scrobble = Scrobble(entry)
        print(
            f"SCROBBLER: found song {scrobble.track.name} played at {scrobble.played_at}"
        )
        insert_scrobble_into_db(scrobble)

    after = time.time_ns() // 1000000  # convert to ms
    return True


def start_scrobbler() -> bool | None:
    # check if auth token is available
    if not bp.session.authorized:
        debugprint(
            "SCROBBLER: session unauthorized, could not enable scrobbler, exiting"
        )
        return False

    debugprint("SCROBBLER: session authorized, enabling scrobbler")
    scrobble()
