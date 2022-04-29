import json
import users_dao
import datetime

from db import db
from flask import Flask, request

db_filename = "auth.db"
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
    Endpoint for creating a new playlist from Spotify with specified length\n
    Request body:\n
    \t- hours: Hours component of playlist length
    \t- minutes: Minutes component of playlist length \n
    Returns:\n 
    \t- TODO: ADD RETURNED DATA HERE
    """
    # verify user

    was_successful, session_token = extract_token(request)

    if not was_successful:
        return session_token

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")

    # create playlist

    body = json.loads(request.data)
    hours = body.get("hours")
    minutes = body.get("minutes")

    if hours is None or minutes is None:
        return failure_response("Request body is missing hours or minutes")

    pass


@app.route("/tempo/playlist/<playlist_id>/")
def get_playlist_songs(playlist_id):
    """
    Endpoint for getting a list of songs in a playlist using the playlist's id.

    Args: 
        playlist_id (int): id of the playlist
    
    No request body.
    
    Returns: TODO 
    """
    #TODO
    pass


@app.route("/tempo/playlist/<playlist_id>/favorite/", methods=["POST"])
def make_favorite(playlist_id):
    """
    Endpoint for "favoriting a playlist" by adding playlist (using id) to playlists table. 
    
    Args: 
        playlist_id (int): id of the playlist

    No request body. 
    
    Returns: TODO 
    """
    #TODO 
    pass
    

@app.route("/tempo/playlist/<playlist_id>/edit/", methods=["POST"])
def edit_playlist_name(playlist_id):
    """
    Endpoint for editing name of a favorited playlist by playlist's id. 
    
    Args: 
        playlist_id (int): id of the playlist

    Request body: 
        title: new title for the playlist 
    
    Returns: TODO 
    """
    #TODO
    pass
    


@app.route("/tempo/playlist/<playlist_id>/", methods=["DELETE"])
def delete_playlist(playlist_id):
    """
    Endpoint for deleting a playlist by id. 
    
    Args: 
        playlist_id (int): id of the playlist

    No request body. 
    
    Returns: TODO 
    """
    #TODO
    pass

# ------------- RUN APP -------------


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
