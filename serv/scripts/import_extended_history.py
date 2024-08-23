#!/usr/bin/env python3

import sys
import time
import json
import datetime
import requests
from utils.config import Config
from db import db
from db.scrobble import Scrobble, Track


def transform_dict(dictionary):
    return {
        "timestamp": dictionary["ts"],
        "username": dictionary["username"],
        "platform": dictionary["platform"],
        "ms_played": dictionary["ms_played"],
        "conn_country": dictionary["conn_country"],
        "ip_address": dictionary["ip_addr_decrypted"],
        "user_agent": dictionary["user_agent_decrypted"],
        "track_name": dictionary["master_metadata_track_name"],
        "artist_name": dictionary["master_metadata_album_artist_name"],
        "album_name": dictionary["master_metadata_album_album_name"],
        "track_uri": dictionary["spotify_track_uri"],
        "episode_name": dictionary["episode_name"],
        "episode_show_name": dictionary["episode_show_name"],
        "episode_uri": dictionary["spotify_episode_uri"],
        "reason_start": dictionary["reason_start"],
        "reason_end": dictionary["reason_end"],
        "shuffle": dictionary["shuffle"],
        "skipped": dictionary["skipped"],
        "offline": dictionary["offline"],
        "offline_timestamp": datetime.datetime.fromtimestamp(
            dictionary["offline_timestamp"]
            / 1000  # spotify timestamps are in milliseconds
        ),
        "incognito_mode": dictionary["incognito_mode"],
    }


def extract_track_id(track_uri):
    return track_uri.split(":")[-1]


def craft_scrobble(dictionary):
    # we are assuming the scrobble has already been validated as a "proper play"
    track_id = extract_track_id(dictionary["track_uri"])

    try:
        track_info = requests.get(
            f"http://localhost:{Config.get(Config.Keys.PORT)}/info/track/{track_id}"
        )
        print(f"Track info: {track_info.text}")
        return Scrobble(
            {
                "track": track_info.json(),
                "played_at": dictionary["timestamp"],
            }
        )
    except json.JSONDecodeError as e:
        print(f"Error: {e}")
        return None


def is_valid_scrobble(item):
    # Ok, this is kinda complicated. I matched both the data collected by this program and the data
    # returned by Spotify, and it seems that the public API i use in this app returns SOME songs
    # whose reasons for ending are classified as "endplay" in the archive i downloaded. Why is this?
    # For brevity, I'm only including songs whose endings are classified as "trackdone" in the
    # database. See why this is the case...

    return item["track_uri"] is not None and item["reason_end"] == "trackdone"


def main():
    # We only initialize this table here as this is the first instance it is needed
    db.database.create_tables([db.ExtendedHistory])

    # concatenate all the arguments' values into a single JSON
    for arg in sys.argv[1:]:
        with open(arg) as f:
            print(f"Importing {arg}")

            data = [transform_dict(dictionary) for dictionary in json.load(f)]
            db.ExtendedHistory.insert_many(data).execute()

            for item in data:
                if is_valid_scrobble(item):
                    print(
                        f"Inserting scrobble {item["track_uri"]}@{item["timestamp"]}"
                    )

                    scrobble = None
                    while scrobble := craft_scrobble(item) is None:
                        print("Waiting for track info...")
                        time.sleep(1)

                    db.insert_scrobble_into_db(scrobble, update_genre=False)

                    # Avoid rate limiting
                    time.sleep(1.75)

            print(f"Imported {arg}")


if __name__ == "__main__":
    main()
