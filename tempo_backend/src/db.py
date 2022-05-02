import datetime
import hashlib
import os
import bcrypt
from sqlalchemy import null, delete

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ------------- TABLES -------------

class User(db.Model):
    """
    User model

    Has 1-to-many relationship with Playlist model
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # user information
    username = db.Column(db.String, nullable=False, unique=True)
    """Username of user, same as the user's Spotify's username"""

    # session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    # association information
    playlists = db.relationship(
        "Playlist",
        cascade="delete"
    )
    """User model has 1-to-many relationship with Playlist model"""

    def __init__(self, **kwargs):
        """
        Initializes a User object

        kwargs:
            username (str): Username of Spotify user
            session_token (str): Session token of Spotify user
            session_expiration (str): Session expiration datetime of Spotify user
            update_token (str): Update token of Spotify user
        """
        self.username = kwargs.get("username")
        self.session_token = kwargs.get("session_token")
        self.session_expiration = kwargs.get("session_expiration")
        self.update_token = kwargs.get("update_token")
        self.renew_session()

    def serialize(self):
        """
        Serialize User object, includes all object fields
        """
        return {
            "id": self.id,
            "username": self.username,
            "session_token": self.session_token,
            "session_expiration": self.session_expiration,
            "playlists": [p.simple_serialize() for p in self.playlists]
        }

    def _urlsafe_base_64(self):
        """
        Randomly generates hashed tokens (used for session/update tokens)
        """
        return hashlib.sha1(os.urandom(64)).hexdigest()

    def renew_session(self):
        """
        Renews the sessions of the user
        """
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        self.update_token = self._urlsafe_base_64()

    def verify_session_token(self, session_token):
        """
        Verifies the session token of a user
        """
        return session_token == self.session_token and datetime.datetime.now() < self.session_expiration

    def verify_update_token(self, update_token):
        """
        Verifies the update token of a user
        """
        return update_token == self.update_token


class Playlist(db.Model):
    """
    Playlist model

    Has many-to-1 relationship with User model
    """
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # playlist information
    sum_length = db.Column(db.Integer, nullable=False)
    """Total sum. length of tracks in playlist"""

    title = db.Column(db.String, nullable=False)
    """
    Title of playlist
    
    "" if playlist is unfavorited
    """

    history = db.Column(db.DateTime)
    """
    Time when the plyalist was last played
    
    None if playlist was never played before
    """

    # association information
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    """Playlist model has many-to-1 relationship with User model"""

    tracks = db.relationship(
        "Track",
        cascade="delete"
    )
    """Playlist model has 1-to-many relationship with Track model"""

    def __init__(self, **kwargs):
        """
        Initializes a Playlist object

        kwargs:
            sum_length (int): Total sum. length of tracks in playlist
            title (str): Title of playlist, "" if playlist is not favorited
            history (Datetime): Datetime when the playlist was last played, null if playlist was never played before
            user_id (int): User id that Playlist belongs to
        """
        self.sum_length = kwargs.get("sum_length")
        self.title = kwargs.get("title", "")
        self.history = kwargs.get("history")
        self.user_id = kwargs.get("user_id")

    def serialize(self):
        """
        Serialize a Playlist object's fields. 
        """
        return {
            "id": self.id,
            "sum_length": self.sum_length,
            "title": self.title,
            "history": self.history,
            "tracks": [t.simple_serialize() for t in self.tracks]
        }

    def simple_serialize(self):
        """
        Serialize a Playlist object's fields, excludes user_id and tracks fields.
        """
        return {
            "id": self.id,
            "sum_length": self.sum_length,
            "title": self.title,
            "history": self.history
        }

    def tracks_serialize(self):
        """
        Serialize all Playlist object's tracks in track field.
        """
        return {
            "tracks": [s.simple_serialize() for s in self.tracks]
        }


class Track(db.Model):
    """
    Track model    

    Has many-to-1 relationship with Playlist model
    """
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # track information
    spotify_id = db.Column(db.String, nullable=False)

    # association information
    playlist_id = db.Column(db.Integer, db.ForeignKey(
        "playlists.id"), nullable=False)
    """Track model has many-to-1 relationship with Playlist model"""

    def __init__(self, **kwargs):
        """
        Initializes a Playlist object

        kwargs:
            spotify_id (str) = Spotify id of track
            playlist_id (int) = Playlist that Track belongs to
        """
        self.spotify_id = kwargs.get("spotify_id")
        self.playlist_id = kwargs.get("playlist_id")

    def simple_serialize(self):
        """
        Serialize a Track object's fields: id, spotify_id.
        """
        return {
            "spotify_id": self.spotify_id
        }
