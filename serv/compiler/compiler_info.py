from typing import List

from scrobbler.scrobbler import scrobble


class PlayedAlbum:
    def __init__(self, name, play_count):
        self.name = name
        self.play_count = play_count


class PlayedArtist:
    def __init__(self, name, play_count):
        self.name = name
        self.play_count = play_count


class PlayedTrack:
    def __init__(self, name, play_count):
        self.name = name
        self.play_count = play_count


class PlayInfo:
    most_played_albums: List[PlayedAlbum] = []
    most_played_artists: List[PlayedArtist] = []
    most_played_tracks: List[PlayedTrack] = []
    scrobble_count: int = 0
    track_count: int = 0
