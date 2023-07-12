# responsible for compiling all the data into a readable format for the client
# to process (the client should be nothing more than a pretty face for the data that is
# processed and served here; pictures will be problamatic, but we can figure that out later
#
#
# FOR STARTERS !!!!!
# Global:
# Top 10 Most Played Artists
# Top 10 Most Played Albums
# Top 10 Most Played Tracks
# 10 Most Recent Scrobbles
# Total Scrobbles
# Total Listening Time

from utils.utils import repeat, debugprint
from compiler.compiler_info import *
import db
from peewee import fn

# every 600 seconds (10 minutes) we will compile all the data and put it into the database
COMPILER_INTERVAL = 600


@repeat(COMPILER_INTERVAL)
def compile_scrobbles():
    debugprint("COMPILER: starting")

    with db.database:
        GlobalPlayInfo.scrobble_count = db.Scrobble.select().count()
        GlobalPlayInfo.track_count = db.Track.select().count()
        GlobalPlayInfo.listening_time = (
            db.Scrobble.select(fn.SUM(db.Track.duration_ms)).join(db.Track).scalar()
        )

        track_function = fn.COUNT(db.Scrobble.track)
        artist_function = fn.COUNT(db.Artist.id)
        album_function = fn.COUNT(db.Album.id)

        GlobalPlayInfo.ten_most_played_tracks = [
            PlayedTrack(**track)
            for track in (
                db.Scrobble.select(db.Track.name, track_function.alias("play_count"))
                .join(db.Track)
                .group_by(db.Track.name)
                .order_by(track_function.desc())
                .limit(10)
                .dicts()
            )
        ]

        GlobalPlayInfo.ten_most_played_artists = [
            PlayedArtist(**artist)
            for artist in (
                db.Scrobble.select(db.Artist.name, artist_function.alias("play_count"))
                .join(db.Track)
                .join(db.ArtistTrack)
                .join(db.Artist)
                .group_by(db.Artist.id)
                .order_by(artist_function.desc())
                .limit(10)
                .dicts()
            )
        ]

        GlobalPlayInfo.ten_most_played_albums = [
            PlayedAlbum(**album)
            for album in (
                db.Scrobble.select(db.Album.name, album_function.alias("play_count"))
                .join(db.Track)
                .join(db.Album)
                .group_by(db.Album.id)
                .order_by(album_function.desc())
                .limit(10)
                .dicts()
            )
        ]

        GlobalPlayInfo.ten_most_recent_scrobbles = [
            PlayedTrack(**track)
            for track in (
                db.Scrobble.select(db.Track.name, db.Scrobble.played_at)
                .join(db.Track)
                .order_by(db.Scrobble.played_at.desc())
                .limit(10)
                .dicts()
            )
        ]

    debugprint("COMPILER: finished")


def start_compiler():
    compile_scrobbles()
