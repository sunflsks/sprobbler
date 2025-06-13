#!/usr/bin/env python3

import sys
import time
import json
import datetime
import requests
from utils.config import Config
from db import db
from db.scrobble import Scrobble
from alive_progress import alive_bar


def transform_dict(dictionary: dict) -> dict:
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


def extract_track_id(track_uri: str) -> str:
    return track_uri.split(":")[-1]


def craft_scrobbles(list_of_items: list) -> list[Scrobble] | None:
    # we are assuming the scrobbles has already been validated as a "proper play"

    track_ids = ",".join(
        [extract_track_id(item["track_uri"]) for item in list_of_items]
    )

    try:
        track_infos = requests.get(
            f"http://localhost:{Config.get(Config.Keys.PORT)}/info/tracks/{track_ids}"
        )

        # track_infos is a dict with "tracks" as a key, and a list of track info as the value
        # we need to extract the track info from the value

        track_info_and_played_at = []
        for item in list_of_items:
            track_id = extract_track_id(item["track_uri"])
            for track_info in track_infos.json()["tracks"]:
                if track_info["id"] == track_id:
                    track_info_and_played_at.append((item, track_info))
                    break

        scrobbles = []
        for item, track_info in track_info_and_played_at:
            try:
                scrobbles.append(
                    Scrobble(
                        {
                            "track": track_info,
                            "played_at": item["timestamp"],
                        }
                    )
                )
            except IndexError as e:
                # this is a rare error that occurs when the track info is not found; for now, we can skip. TODO - make a good fix
                print(f"Error: {e}")
                continue

        return scrobbles

    except json.JSONDecodeError as e:
        print(f"Error: {e}")
        return None


def is_valid_scrobble(item: dict) -> bool:
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
    data = []
    for arg in sys.argv[1:]:
        with open(arg) as f:
            print(f"Importing {arg}")

            data += [transform_dict(dictionary) for dictionary in json.load(f)]

    print("Updating extended history table...")
    db.ExtendedHistory.insert_many(data).execute()
    print("Done!")

    # first validate, then chunk the validated data into 50-item chunks to avoid rate limiting
    validated_data = [item for item in data if is_valid_scrobble(item)]
    validated_data = [
        item
        for item in validated_data
        if datetime.datetime.fromisoformat(item["timestamp"])
    ]
    chunked_data = [
        validated_data[i : i + 50] for i in range(0, len(validated_data), 50)
    ]

    with alive_bar(len(validated_data)) as bar:
        for items in chunked_data:
            retry_timeout = 2
            scrobbles = craft_scrobbles(items)
            while scrobbles is None:
                print(f"Retrying in {retry_timeout} seconds...")
                scrobbles = craft_scrobbles(items)
                time.sleep(retry_timeout)
                retry_timeout **= 2

            for scrobble in scrobbles:
                try:
                    db.insert_scrobble_into_db(scrobble, update_genre=False)
                    bar()
                except Exception as e:
                    print(
                        f"Error inserting scrobble {scrobble.track}@{scrobble.played_at}: {e}"
                    )
                    continue

            # Avoid rate limiting
            time.sleep(1)


if __name__ == "__main__":
    main()
