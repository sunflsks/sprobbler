from doctest import debug
import time
import json
from venv import logger
from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime

import requests
from web.blueprints.login import bp
from utils.scrobble import Scrobble
from utils.utils import debugprint
from db import insert_scrobble_into_db, update_predicted_genre_for_track, Track

# it seems a song is only registered when fully, 100 percent played; partial plays do not count
# as a recently played song. however, if fast forwarded to the end it DOES count.

# how many seconds between each call to api
SPOTIFY_RECENTLY_PLAYED_URL = "/v1/me/player/recently-played"
SPOTIFY_RECENTLY_PLAYED_LIMIT = 50  # maximum value, who knows maybe the user is crazy

after = time.time_ns() // 1000000  # convert to ms


@shared_task(ignore_result=True)
def start_scrobbler() -> bool | None:
    global after

    # check if auth token is available
    if not bp.session.authorized:
        debugprint(
            "SCROBBLER: session unauthorized, could not enable scrobbler, exiting"
        )
        return False

    print("SCROBBLER: session authorized, enabling scrobbler")

    print(f"SCROBBLER: starting @ {datetime.fromtimestamp(after/1000).isoformat()}")

    params = {"limit": SPOTIFY_RECENTLY_PLAYED_LIMIT, "after": after}
    after = time.time_ns() // 1000000  # convert to ms
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

    return True
