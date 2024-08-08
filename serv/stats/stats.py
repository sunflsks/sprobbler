from __future__ import annotations

import peewee
from peewee import fn
from re import T
import datetime
from db.db import database, Scrobble, Track, Album, ArtistTrack, Artist


def highest_day_stats(starting, timedelta):
    with database:
        highest_day_stats = (
            Scrobble.select(
                fn.COUNT(Scrobble.played_at).alias("play_count"),
                fn.DATE_TRUNC("day", Scrobble.played_at).alias("day"),
            )
            .group_by(fn.DATE_TRUNC("day", Scrobble.played_at))
            .order_by(fn.COUNT(Scrobble.played_at).desc())
            .where(Scrobble.played_at > (starting - timedelta))
            .first()
        )

    return {
        "date": highest_day_stats.day,
        "play_count": highest_day_stats.play_count,
    }


def average_play_stats(start, timedelta):
    interval = None

    match timedelta.days:
        case 7:
            interval = 7
        case 30:
            interval = 6
        case 365:
            interval = 12
        case _:
            interval = 6

    with database:
        new_timedelta = timedelta / interval
        avg = []
        for i in range(0, interval):
            end = start - new_timedelta

            avg.append(
                {
                    "count": round(
                        (
                            Scrobble.select(
                                fn.COUNT(Scrobble.played_at).alias("play_count")
                            )
                            .where(Scrobble.played_at.between(end, start))
                            .scalar()
                        )
                        / new_timedelta.days
                    ),
                    "start": end,  # Switch these two, as it flows better chronologically (start -> end, start is earlier than end)
                    "end": start,
                }
            )
            start = end
        return avg


def timedelta_for_alltime():
    with database:
        current_datetime = datetime.datetime.now().astimezone()
        first_scrobble_datetime = (
            Scrobble.select(fn.MIN(Scrobble.played_at).alias("first")).get().first
        )
        return current_datetime - first_scrobble_datetime


def genre_stats(
    starting=datetime.datetime.now(), timedelta=datetime.timedelta(days=30)
):
    with database:
        cur = database.execute_sql(
            """
			SELECT genre, COUNT(genre) AS count FROM track 
			CROSS JOIN LATERAL jsonb_array_elements_text(track.predicted_genre) AS genre 
			JOIN scrobble ON scrobble.track_id = track.id
			WHERE (track.predicted_genre IS NOT NULL) AND (scrobble.played_at > %s) 
			GROUP BY genre;
			""",
            ((starting - timedelta),),
        )

        return [{"genre": row[0], "count": row[1]} for row in cur]


def listening_stats(
    starting=datetime.datetime.now(), timedelta=datetime.timedelta(days=30)
):
    with database:
        listening_dictionary = (
            Scrobble.select(
                fn.date_part("hour", Scrobble.played_at).alias("hour"),
                fn.COUNT(fn.date_part("hour", Scrobble.played_at)).alias("count"),
            )
            .group_by(peewee.SQL("hour"))
            .where(Scrobble.played_at > (starting - timedelta))
            .dicts()
        )

        listening_list = {
            int(row["hour"]): row["count"] for row in listening_dictionary
        }

        return listening_list


def stats_for_timedelta(
    starting=datetime.datetime.now(), timedelta=datetime.timedelta(days=30)
):
    if timedelta is None:
        # seconds since epoch
        timedelta = datetime.timedelta(seconds=datetime.datetime.now().timestamp())

    with database:
        stats = {
            "avg_scrobbles_per_day": round(
                Scrobble.select()
                .where(Scrobble.played_at > (starting - timedelta))
                .count()
                / timedelta.days,
            ),
            "listening_time_ms": Scrobble.select(fn.SUM(Track.duration_ms))
            .join(Track)
            .where(Scrobble.played_at > (starting - timedelta))
            .scalar(),
            "num_artists": Scrobble.select(
                fn.COUNT(fn.DISTINCT(Artist.id)).alias("count")
            )
            .where(Scrobble.played_at > (starting - timedelta))
            .join(Track)
            .join(ArtistTrack)
            .join(Artist)
            .get()
            .count,
            "num_albums": Scrobble.select(
                fn.COUNT(fn.DISTINCT(Album.id)).alias("count")
            )
            .where(Scrobble.played_at > (starting - timedelta))
            .join(Track, on=(Scrobble.track == Track.id))
            .join(Album, on=(Track.album == Album.id))
            .get()
            .count,
            "num_tracks": Scrobble.select(
                fn.COUNT(fn.DISTINCT(Track.id)).alias("count")
            )
            .join(Track)
            .where(Scrobble.played_at > (starting - timedelta))
            .get()
            .count,
            "highest_day": highest_day_stats(starting, timedelta),
            "averages": average_play_stats(starting, timedelta),
            "genre_stats": genre_stats(starting, timedelta),
            "hourly_listening": listening_stats(starting, timedelta),
        }

        return stats
