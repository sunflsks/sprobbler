import db
import datetime


class PlayedArtist:
    def __init__(self, name, play_count, id):
        self.name = name
        self.play_count = play_count
        self.id = id


def ten_most_played_artists_timedelta(starting=datetime.datetime.now(), timedelta=None):
    with db.database:
        if timedelta is None:
            return [
                PlayedArtist(**artist)
                for artist in (db.Artist.ten_most_played_artists().dicts())
            ]

        return [
            PlayedArtist(**artist)
            for artist in (
                db.Artist.ten_most_played_artists_timedelta(
                    starting=starting, timedelta=timedelta
                ).dicts()
            )
        ]
