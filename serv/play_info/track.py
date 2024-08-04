import db
import datetime
from peewee import fn


class PlayedTrack:
    def __init__(self, name, cover_image_url, play_count=None, played_at=None, id=None):
        self.name = name
        self.cover_image_url = cover_image_url
        if play_count:
            self.play_count = play_count
        if played_at:
            self.played_at = played_at
        if id:
            self.id = id


class TrackScrobbleInfo:
    def __init__(self, scrobble_count, track_count, listening_time):
        self.scrobble_count = scrobble_count
        self.track_count = track_count
        self.listening_time = listening_time


def scrobbles_paginated(start, count):
    with db.database:
        ret = [
            PlayedTrack(**track)
            for track in db.Track.scrobbles_paginated(start, count).dicts()
        ]

        return ret


def ten_most_recent_scrobbles():
    return [
        PlayedTrack(**track) for track in (db.Track.ten_most_recent_scrobbles().dicts())
    ]


def ten_most_played_tracks_timedelta(starting=datetime.datetime.now(), timedelta=None):
    with db.database:
        if timedelta is None:
            return [
                PlayedTrack(**track)
                for track in (db.Track.ten_most_played_tracks().dicts())
            ]

        return [
            PlayedTrack(**track)
            for track in (
                db.Track.ten_most_played_tracks_timedelta(
                    starting=starting, timedelta=timedelta
                ).dicts()
            )
        ]


def track_scrobble_info():
    with db.database:
        return TrackScrobbleInfo(
            db.Scrobble.select().count(),
            db.Track.select().count(),
            db.Scrobble.select(fn.SUM(db.Track.duration_ms)).join(db.Track).scalar(),
        )
