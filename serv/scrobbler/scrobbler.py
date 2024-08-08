from doctest import debug
import json
from venv import logger
from celery import shared_task
from datetime import datetime, timezone, timedelta

import requests
from web.blueprints.login import bp
from db.scrobble import Scrobble
from utils.utils import debugprint
from db.db import insert_scrobble_into_db

SECONDS_TO_MS = 1_000

# it seems a song is only registered when fully, 100 percent played; partial plays do not count
# as a recently played song. however, if fast forwarded to the end it DOES count.

# how many seconds between each call to api
SPOTIFY_RECENTLY_PLAYED_URL = "/v1/me/player/recently-played"
SPOTIFY_RECENTLY_PLAYED_LIMIT = 30


@shared_task(ignore_result=True)
def start_scrobbler() -> bool | None:
    # check if auth token is available
    if not bp.session.authorized:
        debugprint(
            "SCROBBLER: session unauthorized, could not enable scrobbler, exiting"
        )
        return False

    logger.info("SCROBBLER: session authorized, enabling scrobbler")

    cur_datetime = datetime.now(timezone.utc)

    print(f"SCROBBLER: starting @ {cur_datetime.isoformat()}")

    params = {
        "limit": SPOTIFY_RECENTLY_PLAYED_LIMIT,
        "before": round(cur_datetime.timestamp() * SECONDS_TO_MS),
    }

    try:
        resp = bp.session.get(SPOTIFY_RECENTLY_PLAYED_URL, params=params)
    except requests.exceptions.RequestException as err:
        print(f"ERROR: Could not get recently played songs: {err}")
        return False

    if resp.status_code != 200:
        debugprint(f"SCROBBLER: get was not successful: {resp}")
        print(f"{resp.text}")
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
