import db


class PlayedAlbum:
    def __init__(self, name, play_count, cover_image_url):
        self.name = name
        self.play_count = play_count
        self.cover_image_url = cover_image_url


def ten_most_played_albums():
    return [
        PlayedAlbum(**album) for album in (db.ten_most_played_albums.select().dicts())
    ]
