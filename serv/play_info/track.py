import db
from peewee import fn


class PlayedTrack:
    def __init__(
        self, name, cover_image_url, play_count=None, played_at=None, track_id=None
    ):
        self.name = name
        self.cover_image_url = cover_image_url
        if play_count:
            self.play_count = play_count
        if played_at:
            self.played_at = played_at
        if track_id:
            self.track_id = track_id


class TrackScrobbleInfo:
    def __init__(self, scrobble_count, track_count, listening_time):
        self.scrobble_count = scrobble_count
        self.track_count = track_count
        self.listening_time = listening_time


def scrobbles_between_timestamps(start, end):
    with db.database:
        return [
            PlayedTrack(**track)
            for track in (
                db.scrobbles_by_timestamp.select()
                .where(
                    start <= db.scrobbles_by_timestamp.played_at,
                    db.scrobbles_by_timestamp.played_at <= end,
                )
                .dicts()
            )
        ]


def scrobbles_paginated(start, count):
    with db.database:
        return [
            PlayedTrack(**track)
            for track in (
                db.scrobbles_by_timestamp.select()
                .where(
                    db.scrobbles_by_timestamp.played_at <= start,
                )
                .limit(count)
                .dicts()
            )
        ]


def ten_most_recent_scrobbles():
    return [
        PlayedTrack(**track)
        for track in (db.ten_most_recent_scrobbles.select().dicts())
    ]


def ten_most_played_tracks():
    return [
        PlayedTrack(**track) for track in (db.ten_most_played_tracks.select().dicts())
    ]


def track_scrobble_info():
    with db.database:
        return TrackScrobbleInfo(
            db.Scrobble.select().count(),
            db.Track.select().count(),
            db.Scrobble.select(fn.SUM(db.Track.duration_ms)).join(db.Track).scalar(),
        )
