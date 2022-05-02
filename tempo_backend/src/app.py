import json
import users_dao
import datetime

from db import db
from flask import Flask, request
from db import User

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
    

@app.route("/tempo/login/",methods=["POST"])
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
            "session_token":user.session_token,
            "session_expiration":str(user.session_expiration),
            "update_token": user.update_token
        },201
    )





@app.route("/tempo/<int:user_id>/",methods=["GET"])
def get_user_token(user_id):
    """
    Endpoint for returning token associated with the user
    """

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")

    tok=user.session_token

    return tok


@app.route("/tempo/playlist/",methods=["GET"])
def get_favorite_playlist_songs():
    """
    Endpoint for getting all previously favorited songs from database
    """
    return success_response({"playlists": [p.simple_serialize() for p in Playlist.query.all()]})

# ------------- RUN APP -------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
