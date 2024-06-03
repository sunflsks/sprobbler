import db


class PlayedArtist:
    def __init__(self, name, play_count):
        self.name = name
        self.play_count = play_count


def ten_most_played_artists():
    return [
        PlayedArtist(**artist)
        for artist in (db.ten_most_played_artists.select().dicts())
    ]
