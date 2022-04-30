import json
import users_dao
import datetime

from db import db
from flask import Flask, request

db_filename = "tempo.db"
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    """
    Generalized success response function
    """
    return json.dumps(data), code


def failure_response(message, code=404):
    """
    Generalized failure response function
    """
    return json.dumps({"error": message}), code

# helper for managing tokens


def extract_token(request):
    """
    Helper function that extracts the token from the header of a request
    """
    auth_header = request.headers.get("Authorization")

    if auth_header is None:
        return False, json.dumps({"Missing authorization header"})

    bearer_token = auth_header.replace("Bearer", "").strip()

    return True, bearer_token


# ------------- ROUTES -------------

@app.route("/")
@app.route("/tempo/playlist/", methods=["POST"])
def create_new_playlist():
    """
    Endpoint for creating a new playlist from Spotify with specified length

    Returns:
        list: List of tracks with total playtime of specified length
    """

    # verify user

    was_successful, session_token = extract_token(request)

    if not was_successful:
        return session_token

    user = users_dao.get_user_by_session_token(session_token)
    # TODO: if statment to check for invalid session tokens
    if not user or True:
        return failure_response("Invalid session token")

    # create playlist

    body = json.loads(request.data)
    hours = body.get("hours")
    minutes = body.get("minutes")

    if hours is None or minutes is None:
        return failure_response("Request body is missing hours or minutes")

    # * pseudocode for creating a playlist w/ given length
    """
    int length = int(hours)*60 + int(minutes)
    get recommended tracks request: 
        # of tracks = 100
        max length of track = length
    recommended = list of recommended tracks from Spotify
    playlist = findTracklistSum(recommended, length)
    return playlist as json list of tracks (or whatever FE needs to get the song from Spotify)
    """

    pass


def find_tracklist_sum(tracklist, sum, increment_fuzzy=60):
    """    
    Find a sublist of tracklist with total playtime equal to given value sum

    Args:
        tracklist (list): List of tracks
        sum (int): Target sum to find in seconds
        increment_fuzzy (int, optional): Number of seconds to increment fuzzy by. Defaults to 60.

    Returns:
        list: List of tracks with total playtime equal to given value sum
    """
    playlist = []
    fuzzy = 0
    while len(playlist) == 0:
        playlist = find_tracklist_sum_helper(
            tracklist, len(tracklist), sum, fuzzy)
        increment_fuzzy += 60

    return playlist


def find_tracklist_sum_helper(tracks, n, sum, fuzzy):
    """
    Helper function for finding tracklist with total playtime equal to given value sum

    Returns empty list if one is not found

    Args:
        tracks (list): List where tracks to be searched through
        n (int): Length of tracks
        sum (int): Target sum to find in seconds
        fuzzy (int): Leniency on how close the tracklist playtime and sum should be in seconds

    Returns:
        list: List of tracks with total playtime equal to given value sum or empty list if one is not found
    """
    if n == 0:
        return []

    last_track = tracks[n-1]
    last_length = last_track["duration_ms"]/1000

    if abs(sum - last_length) <= fuzzy:
        return [last_track]

    keep_last = find_tracklist_sum_helper(tracks, n-1, sum-last_length, fuzzy)
    skip_last = find_tracklist_sum_helper(tracks, n-1, sum, fuzzy)

    if not len(keep_last) == 0:
        keep_last += [last_track]

    if len(keep_last) == 0:
        return skip_last
    else:
        return keep_last


# ------------- RUN APP -------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
