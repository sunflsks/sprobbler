import json
import datetime
from db import stats_for_timedelta
from flask import Blueprint, abort
from play_info import albums, artists, track, utils

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
            timedelta = None
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

    return json.dumps(report, cls=utils.PlayedItemsJSONEncoder)
