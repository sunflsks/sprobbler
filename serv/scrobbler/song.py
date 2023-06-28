# going off the contents of an Entry in the spotify API docs; maybe not very ideal but not horrible

# API return values -
# track
#   album
#       album_type: type of album (string, can either be album single or compilation)
#       total_tracks : total # of tracks in album (int)
# played_at: timestamp (string, iso8601 UTC)


class Song:
    def __init__(self, entry):
        self.track = entry["track"]["name"]
        self.played_at = entry["played_at"]
