# going off the contents of an Entry in the spotify API docs; maybe not very ideal but not horrible

# API return values (that i need) -
# track
#   album
#       album_type: type of album (string, can either be album single or compilation)
#   artists [array]
#       name: name of artist (string)
#   explicit: whether explicit (bool)
#   name: name of track (string)
#   popularity: popularity of track (int)
# played_at: timestamp (string, iso8601 UTC)

from datetime import datetime


class Album:
    def __init__(self, album_dict):
        self.album_type = album_dict["album_type"]
        self.id = album_dict["id"]
        self.name = album_dict["name"]


class Artist:
    def __init__(self, artist_dict):
        self.name = artist_dict["name"]
        self.id = artist_dict["id"]


class Track:
    def __init__(self, track_dict):
        self.album = Album(track_dict["album"])
        self.artists = [Artist(artist) for artist in track_dict["artists"]]
        self.explicit = track_dict["explicit"]
        self.name = track_dict["name"]
        self.popularity = track_dict["popularity"]
        self.id = track_dict["id"]
        self.duration_ms = track_dict["duration_ms"]


class Scrobble:
    def __init__(self, entry):
        self.track = Track(entry["track"])
        self.played_at = datetime.fromisoformat(entry["played_at"])
