import db


class PlayedAlbum:
    def __init__(self, name, play_count, cover_image_url, id):
        self.name = name
        self.play_count = play_count
        self.cover_image_url = cover_image_url
        self.id = id


def ten_most_played_albums_past_days(days=30):
    if days is None:
        return [
            PlayedAlbum(**album)
            for album in (db.Album.ten_most_played_albums().dicts())
        ]

    return [
        PlayedAlbum(**album)
        for album in (db.Album.ten_most_played_albums_past_days(days).dicts())
    ]
