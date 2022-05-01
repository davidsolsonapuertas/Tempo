import json
import users_dao
import datetime
import requests

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
    Endpoint for creating a new playlist from Spotify with specified playtime

    Returns:
        json: JSON containing list of tracks with total playtime of specified length
    """

    # verify user

    was_successful, session_token = extract_token(request)

    if not was_successful:
        return session_token

    user = users_dao.get_user_by_session_token(session_token)
    if not user:
        return failure_response("User not found")

    # create playlist

    body = json.loads(request.data)
    hours = body.get("hours")
    minutes = body.get("minutes")

    if hours is None or minutes is None:
        return failure_response("Request body is missing hours or minutes", 400)

    playtime_sec = int(hours)*60*60 + int(minutes)*60
    
    top_artists_response = request.get(
        "https://api.spotify.com/v1/me/top/type/artists",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + session_token
        },
        data={
            "limit": 5
        }
    ).json()
    if not top_artists_response["error"] is None:
        return failure_response(top_artists_response["error"]["message"], top_artists_response["error"]["status"])
    
    top_genre_response = request.get(
        "https://api.spotify.com/v1/recommendations/available-genre-seeds",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + session_token
        }
    ).json()
    if not top_genre_response["error"] is None:
        return failure_response(top_genre_response["error"]["message"], top_genre_response["error"]["status"])

    top_tracks_response = request.get(
        "https://api.spotify.com/v1/me/top/type/tracks",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + session_token
        },
        data={
            "limit": 5
        }
    ).json()    
    if not top_tracks_response["error"] is None:
        return failure_response(top_tracks_response["error"]["message"], top_tracks_response["error"]["status"])
    
    top_artists_list = top_artists_response["items"]
    top_genre_list = top_genre_response["genres"]
    top_tracks_list = top_tracks_response["items"]
    
    seed_artists = ""
    for i in range(len(top_artists_list)):
        seed_artists += top_artists_list[i]["id"]
        if i < 4:
            seed_artists += ","

    seed_genres = ""
    for i in range(len(top_genre_list)):
        seed_genres += top_genre_list[i]
        if i < 4:
            seed_genres += ","

    seed_tracks = ""
    for i in range(len(top_tracks_list)):
        seed_tracks += top_tracks_list[i]["id"]
        if i < 4:
            seed_tracks += ","

    recommendations_response = request.get(
        "https://api.spotify.com/v1/recommendations",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + session_token
        },
        data={
            "seed_artists": seed_artists,
            "seed_genres": seed_genres,
            "seed_tracks": seed_tracks,
            "limit": int(playtime_sec/60)
        }
    ).json()
    if not recommendations_response["error"] is None:
        return failure_response(recommendations_response["error"]["message"], recommendations_response["error"]["status"])

    playlist = find_tracklist_sum(recommendations_response["tracks"], playtime_sec)
    
    return success_response({"tracks": playlist})


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
        fuzzy += increment_fuzzy

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
