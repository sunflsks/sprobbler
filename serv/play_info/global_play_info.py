# responsible for displaying the global play information (the stuff tracked since the start of time)
# the client should be nothing more than a pretty face for the data that is
# processed and served here; pictures will be problamatic, but we can figure that out later
#
#
# FOR STARTERS !!!!!
# Global:
# Total Scrobbles
# Total Listening Time
# Total Artists
#
# Top 10 Most Played Artists
# Top 10 Most Played Albums
# Top 10 Most Played Tracks
# 10 Most Recent Scrobbles

from typing import List
import db
from peewee import fn


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

    def __init__(self):
        with db.database:
            self.scrobble_count = db.Scrobble.select().count()
            self.track_count = db.Track.select().count()
            self.listening_time = (
                db.Scrobble.select(fn.SUM(db.Track.duration_ms)).join(db.Track).scalar()
            )

            track_function = fn.COUNT(db.Scrobble.track)
            artist_function = fn.COUNT(db.Artist.id)
            album_function = fn.COUNT(db.Album.id)

            self.ten_most_played_tracks = [
                PlayedTrack(**track)
                for track in (
                    db.Scrobble.select(
                        db.Track.name,
                        db.Album.cover_image_url,
                        track_function.alias("play_count"),
                    )
                    .join(db.Track)
                    .join(db.Album)
                    .group_by(db.Track.name)
                    .order_by(track_function.desc())
                    .limit(10)
                    .dicts()
                )
            ]

            self.ten_most_played_artists = [
                PlayedArtist(**artist)
                for artist in (
                    db.Scrobble.select(
                        db.Artist.name, artist_function.alias("play_count")
                    )
                    .join(db.Track)
                    .join(db.ArtistTrack)
                    .join(db.Artist)
                    .group_by(db.Artist.id)
                    .order_by(artist_function.desc())
                    .limit(10)
                    .dicts()
                )
            ]

            self.ten_most_played_albums = [
                PlayedAlbum(**album)
                for album in (
                    db.Scrobble.select(
                        db.Album.name,
                        album_function.alias("play_count"),
                        db.Album.cover_image_url,
                    )
                    .join(db.Track)
                    .join(db.Album)
                    .group_by(db.Album.id)
                    .order_by(album_function.desc())
                    .limit(10)
                    .dicts()
                )
            ]

            self.ten_most_recent_scrobbles = [
                PlayedTrack(**track)
                for track in (
                    db.Scrobble.select(
                        db.Track.name, db.Album.cover_image_url, db.Scrobble.played_at
                    )
                    .join(db.Track)
                    .join(db.Album)
                    .order_by(db.Scrobble.played_at.desc())
                    .limit(10)
                    .dicts()
                )
            ]

    def dict_representation(self):
        return {
            "ten_most_played_artists": [
                {"name": artist.name, "play_count": artist.play_count}
                for artist in self.ten_most_played_artists
            ],
            "ten_most_played_albums": [
                {
                    "name": album.name,
                    "play_count": album.play_count,
                    "cover_image_url": album.cover_image_url,
                }
                for album in self.ten_most_played_albums
            ],
            "ten_most_played_tracks": [
                {
                    "name": track.name,
                    "play_count": track.play_count,
                    "cover_image_url": track.cover_image_url,
                }
                for track in self.ten_most_played_tracks
            ],
            "ten_most_recent_scrobbles": [
                {
                    "name": track.name,
                    "played_at": track.played_at,
                    "cover_image_url": track.cover_image_url,
                }
                for track in self.ten_most_recent_scrobbles
            ],
            "scrobble_count": self.scrobble_count,
            "track_count": self.track_count,
            "listening_time": self.listening_time,
        }
