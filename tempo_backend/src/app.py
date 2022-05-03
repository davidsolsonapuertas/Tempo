import json
import users_dao
import datetime
import requests

from db import db
from db import User
from db import Playlist
from db import Track
from flask import Flask, request
from db import User

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
def hello_world():
    """
    Endpoint for hello world

    Returns:
        json: JSON with value "Hello world!"
    """
    return success_response("Hello world!")


@app.route("/tempo/playlist/", methods=["POST"])
def create_new_playlist():
    """
    Endpoint for creating a new playlist from Spotify with specified playtime

    Returns:
        json: JSON containing list of tracks with total playtime of specified length.

        The returned JSON is the same as the one listed on Spotify's API for getting several tracks at once:

        https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-tracks
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
        return failure_response("Request body is missing hours or minutes")


@app.route("/tempo/login/", methods=["POST"])
def store_user_token():
    """
    Endpoint for storing Spotify session tokens for user 

    This function takes in the user's username and adds it to the database if the 
    user does not already exist in there. The user's session_token, session_expiration,
    and update_token are all returned
    """
    body = json.loads(request.data)
    username = body.get("username")

    if username is None:
        return failure_response("Missing username")

    was_successful, user = users_dao.create_user(username)

    if not was_successful:
        return failure_response("User already exists")

    return success_response(
        {
            "session_token": user.session_token,
            "session_expiration": str(user.session_expiration),
            "update_token": user.update_token
        }, 201
    )


@app.route("/tempo/<int:user_id>/", methods=["GET"])
def get_user_token(user_id):
    """
    Endpoint for returning token associated with the user
    """

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")

    tok = user.session_token

    return tok


@app.route("/tempo/playlist/", methods=["POST"])
def create_new_playlist():
    """
    Endpoint for creating a new playlist from Spotify with specified playtime
    Returns:
        json: JSON containing list of tracks with total playtime of specified length.

        The returned JSON is the same as the one listed on Spotify's API for getting several tracks at once:
        https://developer.spotify.com/documentation/web-api/reference/#/operations/get-several-tracks
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

    top_artists_response = requests.get(
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

    top_genre_response = requests.get(
        "https://api.spotify.com/v1/recommendations/available-genre-seeds",
        headers={
            "Content-type": "application/json",
            "Authorization": "Bearer " + session_token
        }
    ).json()
    if not top_genre_response["error"] is None:
        return failure_response(top_genre_response["error"]["message"], top_genre_response["error"]["status"])

    top_tracks_response = requests.get(
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

    recommendations_response = requests.get(
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

    playlist = find_tracklist_sum(
        recommendations_response["tracks"], playtime_sec)

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


@app.route("/tempo/playlist/<user_id>")
def get_playlists(user_id):
    """
    Endpoint for getting all favorited playlists of user using their id.

    Args:
        user_id (int): id of the user in the table
    No request body.

    Returns: 
    """
    return success_response({"playlists": [p.simple_serialize() for p in Playlist.query.filter_by(id=user_id)]})


@app.route("/tempo/playlist/<playlist_id>/")
def get_playlist_tracks(playlist_id):
    """
    Endpoint for getting a list of tracks in a playlist using the playlist's id.
    
    Args: 
        playlist_id (int): id of the playlist
    No request body.

    Returns: json of list of tracks (see api)
    """
    playlist = Playlist.query.filter_by(id=playlist_id).first()
    if playlist is None:
        return failure_response("Playlist was not found!", 404)

    return success_response(playlist.tracks_serialize())


@app.route("/tempo/playlist/<user_id>/favorite/", methods=["POST"])
def make_favorite(user_id):
    """
    Endpoint for "favoriting a playlist" by adding playlist for user (using user_id) 
    to playlists table. 
    
    Args: 
        playlist_id (int): id of the playlist
    Request body: 
    {
        "tracks": [
            <spotify_id> (string),
            <spotify_id> (string), 
            ...
        ]
    }

    Returns: new favorited playlist as json
    """
    body = json.loads(request.data)
    if body is None:
        return failure_response("Must include request body.", 400)
    track_ids = body.get("tracks")
    length = body.get("length")
    if (track_ids is None) or (length is None):
        return failure_response("Must include tracks and length in request body.", 400)

    favorite_playlist = Playlist(
        sum_length=length,
        title="Untitled Playlist",
        history=None,
        user_id=user_id)
    db.session.add(favorite_playlist)

    # add tracks from body to tracks table, which adds them to playlist's col
    for t in track_ids:
        track = Track(
            spotify_id=t,
            playlist_id=favorite_playlist.id
        )
        db.session.add(track)

    db.session.commit()
    return success_response(favorite_playlist.simple_serialize(), 201)


@app.route("/tempo/playlist/<playlist_id>/edit/", methods=["POST"])
def edit_playlist_name(playlist_id):
    """
    Endpoint for editing name of a favorited playlist by playlist's id. 
   
    Args: 
        playlist_id (int): id of the playlist
    Request body: 
        title: new title for the playlist 
    
    Returns: returns json of updated playlist (see api) 
    """
    playlist = playlist = Playlist.query.filter_by(id=playlist_id).first()
    if playlist is None:
        return failure_response("Playlist was not found!", 404)

    body = json.loads(request.data)
    playlist.title = body["title"]
    db.session.commit()
    return success_response(playlist.serialize(), 201)


@app.route("/tempo/playlist/<playlist_id>/", methods=["DELETE"])
def delete_playlist(playlist_id):
    """
    Endpoint for deleting a playlist by id. 
   
    Args: 
        playlist_id (int): id of the playlist
    No request body. 

    Returns: returns success message 
    """
    playlist = Playlist.query.filter_by(id=playlist_id).first()
    if playlist is None:
        return failure_response("Playlist was not found!", 404)

    db.session.delete(playlist)
    db.session.commit()
    return success_response("Playlist deleted")


# ------------- RUN APP -------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
