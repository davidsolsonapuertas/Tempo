import json
import users_dao
import spotipy

from db import db
from db import Playlist
from db import Track
from flask import Flask, request
from spotipy import SpotifyException

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


def get_user_from_token(session_token):
    """
    Returns user id given a session token
    
    Args:
        session_token (string): Session token of the user
    
    Returns:
        string: Spotify id of the user
    """
    sp = spotipy.Spotify(auth=session_token)
    
    try:
        me = sp.current_user()
    except SpotifyException as e:
        error_message = e.msg.split("\n")[1].strip()
        return failure_response(error_message, e.http_status)
    
    user_id = me["id"]

    return user_id

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

    # verify request has header

    was_successful, session_token = extract_token(request)

    if not was_successful:
        return session_token

    # create playlist

    body = json.loads(request.data)
    hours = body.get("hours")
    minutes = body.get("minutes")

    if hours is None or minutes is None:
        return failure_response("Request body is missing hours or minutes", 400)

    playtime_sec = int(hours)*60*60 + int(minutes)*60

    sp = spotipy.Spotify(auth=session_token)

    try:
        recently_played = sp.current_user_recently_played(limit=5)
    except SpotifyException as e:
        error_message = e.msg.split("\n")[1].strip()
        return failure_response(error_message, e.http_status)
    
    seed_tracks = []
    for p in recently_played["items"]:
        seed_tracks.append(p["track"]["id"])
        
    got_playlist = False
    while not got_playlist:
        try:
            recommendations_response = sp.recommendations(limit=100, seed_tracks=seed_tracks)
        except SpotifyException as e:
            error_message = e.msg.split("\n")[1].strip()
            return failure_response(error_message, e.http_status)
        
        playlist, got_playlist = find_tracklist_sum(recommendations_response["tracks"], playtime_sec)
        
    playlist_dur = 0
    for t in playlist:
        playlist_dur += int(t["duration_ms"]/1000)

    return success_response({"tracks": playlist})


def find_tracklist_sum(tracklist, sum, fuzzy=30):
    
    """    
    Find a sublist of tracklist with total playtime equal to given value sum

    Args:
        tracklist (list): List of tracks
        sum (int): Target sum to find in seconds
        fuzzy (int, optional): Leniency on how close the tracklist playtime and sum should be in seconds. Defaults to 30.

    Returns:
        list: List of tracks with total playtime equal to given value sum
        bool: If playlist was found within alloted fuzzy limit
    """
    playlist = []
    time_left = sum
    
    while time_left > 0 and len(tracklist) > 0:
        last_track = tracklist.pop()
        last_length = int(last_track["duration_ms"]/1000)
        playlist.append(last_track)
        time_left -= last_length
    
    while abs(time_left) > fuzzy and len(tracklist) > 0:
        removed_track = playlist.pop()
        removed_length = int(removed_track["duration_ms"]/1000)
        time_left += removed_length
        
        last_track = tracklist.pop()
        last_length = int(last_track["duration_ms"]/1000)
        playlist.append(last_track)
        time_left -= last_length

    return playlist, len(tracklist) > 0

# not used - too slow
def find_tracklist_sum_helper(tracks, n, sum, fuzzy):
    """
    Helper function for finding tracklist with total playtime equal to given value sum

    Returns empty list if one is not found

    Args:
        tracks (list): List of tracks to be searched through
        n (int): Length of tracks
        sum (int): Target sum to find in seconds
        fuzzy (int): Leniency on how close the tracklist playtime and sum should be in seconds

    Returns:
        list: List of tracks with total playtime equal to given value sum or empty list if one is not found
    """
    if n == 0:
        return []
    
    last_track = tracks[n-1]
    last_length = int(last_track["duration_ms"]/1000)

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


@app.route("/tempo/login/", methods=["POST"])
def store_user():
    """
    Endpoint for storing Spotify id for user 

    This function takes in the user's id and username and adds it to the database if the 
    user does not already exist in there. The user's id and username are then returned.
    """
    body = json.loads(request.data)
    id = body.get("id")
    username = body.get("username")

    if username is None:
        return failure_response("Missing username")

    was_successful, user = users_dao.create_user(id, username)

    if not was_successful:
        return failure_response("User already exists")

    return success_response(
        {
            "id": user.id,
            "username": user.username
        }, 201
    )


@app.route("/tempo/playlist/<session_token>/", methods=["GET"])
def get_playlists(session_token):
    """
    Endpoint for getting all favorited playlists of user using their Spotify id.

    Args:
        session_token (string): session token for authorization

    No request body.

    Returns: json of list of user's playlists
    """
    user_id = get_user_from_token(session_token)
    return success_response({"playlists": [p.simple_serialize() for p in Playlist.query.filter_by(id=user_id)]})


@app.route("/tempo/playlist/<playlist_id>/", methods=["GET"])
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


@app.route("/tempo/playlist/<session_token>/favorite/", methods=["POST"])
def make_favorite(session_token):
    """
    Endpoint for "favoriting a playlist" by adding playlist for user (using their session_token) 
    to playlists table.

    Args:
        session_token (string): current session_token of the user
    Request body:
    {
        "tracks": [
            <spotify_id> (string),
            <spotify_id> (string),
            ...],
        "length": <length of playlist> (int)
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

    user_id = get_user_from_token(session_token)

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
