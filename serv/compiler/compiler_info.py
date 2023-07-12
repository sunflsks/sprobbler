from typing import List

from scrobbler.scrobbler import scrobble


class PlayedAlbum:
    def __init__(self, name, play_count, cover_image_url):
        self.name = name
        self.play_count = play_count
        self.cover_image_url = cover_image_url


class PlayedArtist:
    def __init__(self, name, play_count):
        self.name = name
        self.play_count = play_count


class PlayedTrack:
    def __init__(self, name, cover_image_url, play_count=None, played_at=None):
        self.name = name
        self.cover_image_url = cover_image_url
        if play_count:
            self.play_count = play_count
        if played_at:
            self.played_at = played_at


class GlobalPlayInfo:
    ten_most_played_artists: List[PlayedArtist] = []
    ten_most_played_albums: List[PlayedAlbum] = []
    ten_most_played_tracks: List[PlayedTrack] = []

    ten_most_recent_scrobbles: List[PlayedTrack] = []
    scrobble_count: int = 0
    track_count: int = 0
    listening_time: int = 0  # in milliseconds

    @classmethod
    def dict_representation(cls):
        return {
            "ten_most_played_artists": [
                {"name": artist.name, "play_count": artist.play_count}
                for artist in cls.ten_most_played_artists
            ],
            "ten_most_played_albums": [
                {
                    "name": album.name,
                    "play_count": album.play_count,
                    "cover_image_url": album.cover_image_url,
                }
                for album in cls.ten_most_played_albums
            ],
            "ten_most_played_tracks": [
                {
                    "name": track.name,
                    "play_count": track.play_count,
                    "cover_image_url": track.cover_image_url,
                }
                for track in cls.ten_most_played_tracks
            ],
            "ten_most_recent_scrobbles": [
                {
                    "name": track.name,
                    "played_at": track.played_at,
                    "cover_image_url": track.cover_image_url,
                }
                for track in cls.ten_most_recent_scrobbles
            ],
            "scrobble_count": cls.scrobble_count,
            "track_count": cls.track_count,
            "listening_time": cls.listening_time,
        }
