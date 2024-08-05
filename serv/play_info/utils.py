import decimal
import datetime
from flask.json.provider import DefaultJSONProvider
from play_info.track import PlayedTrack
from play_info.albums import PlayedAlbum
from play_info.artists import PlayedArtist


class PlayedItemsJSONProvider(DefaultJSONProvider):
    def __init__(self, app):
        super().__init__(app)

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)

        if isinstance(o, datetime.datetime):
            # automatically add all timezone info for clients that expect it
            return o.astimezone().isoformat(timespec="seconds")

        if isinstance(o, PlayedAlbum):
            return {
                "name": o.name,
                "play_count": o.play_count,
                "cover_image_url": o.cover_image_url,
                "id": o.id,
            }

        if isinstance(o, PlayedArtist):
            return {"name": o.name, "play_count": o.play_count, "id": o.id}

        if isinstance(o, PlayedTrack):
            played_track_dict = {
                "name": o.name,
                "cover_image_url": o.cover_image_url,
                "id": o.id,
            }

            for field in ("play_count", "played_at", "track_id"):
                if hasattr(o, field):
                    played_track_dict[field] = getattr(o, field)

            return played_track_dict

        return super().default(o)
