import db
import datetime


class PlayedAlbum:
    def __init__(self, name, play_count, cover_image_url, id):
        self.name = name
        self.play_count = play_count
        self.cover_image_url = cover_image_url
        self.id = id


def ten_most_played_albums_timedelta(starting=datetime.datetime.now(), timedelta=None):
    if timedelta is None:
        return [
            PlayedAlbum(**album)
            for album in (db.Album.ten_most_played_albums().dicts())
        ]

    return [
        PlayedAlbum(**album)
        for album in (
            db.Album.ten_most_played_albums_timedelta(
                starting=starting, timedelta=timedelta
            ).dicts()
        )
    ]
