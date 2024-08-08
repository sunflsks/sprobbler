import datetime
from stats.stats import stats_for_timedelta, timedelta_for_alltime
from flask import Blueprint, abort, jsonify
from stats import albums, artists, track

bp = Blueprint("reports", __name__)


@bp.route("/<string:report_type>")
def reports(report_type):
    print(report_type)
    timedelta = None  # past days to generate report for

    match report_type:
        case "weekly":
            timedelta = datetime.timedelta(7)
        case "monthly":
            timedelta = datetime.timedelta(30)
        case "yearly":
            timedelta = datetime.timedelta(365)
        case "alltime":
            timedelta = timedelta_for_alltime()
        case _:
            abort(404)

    report = {
        "report_type": report_type,
        "ten_most_played_artists": artists.ten_most_played_artists_timedelta(
            timedelta=timedelta
        ),
        "ten_most_played_albums": albums.ten_most_played_albums_timedelta(
            timedelta=timedelta
        ),
        "ten_most_played_tracks": track.ten_most_played_tracks_timedelta(
            timedelta=timedelta
        ),
        "stats": stats_for_timedelta(timedelta=timedelta),
    }

    return jsonify(report)
