import db


class PlayedArtist:
    def __init__(self, name, play_count, id):
        self.name = name
        self.play_count = play_count
        self.id = id


def ten_most_played_artists():
    return [
        PlayedArtist(**artist)
        for artist in (db.Artist.ten_most_played_artists().dicts())
    ]
