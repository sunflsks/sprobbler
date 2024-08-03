import json
from flask import Blueprint, abort
from play_info import albums, artists, track, utils

bp = Blueprint("reports", __name__)


@bp.route("/<string:report_type>")
def reports(report_type):
    print(report_type)
    time_range = None  # past days to generate report for

    match report_type:
        case "weekly":
            time_range = 7
        case "monthly":
            time_range = 30
        case "yearly":
            time_range = 365
        case "alltime":
            time_range = None
        case _:
            abort(404)

    report = {
        "report_type": report_type,
        "ten_most_played_artists": artists.ten_most_played_artists_past_days(
            time_range
        ),
        "ten_most_played_albums": albums.ten_most_played_albums_past_days(time_range),
        "ten_most_played_tracks": track.ten_most_played_tracks_past_days(time_range),
    }

    return json.dumps(report, cls=utils.PlayedItemsJSONEncoder)
