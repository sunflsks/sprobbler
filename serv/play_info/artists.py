import db


class PlayedArtist:
    def __init__(self, name, play_count, id):
        self.name = name
        self.play_count = play_count
        self.id = id


def ten_most_played_artists_past_days(days=30):
    with db.database:
        if days is None:
            return [
                PlayedArtist(**artist)
                for artist in (db.Artist.ten_most_played_artists().dicts())
            ]

        return [
            PlayedArtist(**artist)
            for artist in (db.Artist.ten_most_played_artists_past_days(days).dicts())
        ]
