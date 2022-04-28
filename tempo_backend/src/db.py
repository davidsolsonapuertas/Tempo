import datetime
import hashlib
import os
import bcrypt
from sqlalchemy import null

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

    def renew_session(self):
        """
        TODO
        Renews the sessions of the user
        """
        pass

    def verify_session_token(self, session_token):
        """
        TODO
        Verifies the session token of a user
        """
        pass

    def verify_update_token(self, update_token):
        """
        TODO
        Verifies the update token of a user
        """
        pass


class Playlist(db.Model):
    """
    Playlist model
    
    Has many-to-1 relationship with User model
    """
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # playlist information
    sum_length = db.Column(db.Integer, nullable=False)
    """Total sum. length of songs in playlist"""

    title = db.Column(db.String, nullable=False)
    """
    Title of playlist
    
    "" if playlist is unfavorited
    """

    history = db.Column(db.DateTime)
    """
    Time when the plyalist was last played
    
    null if playlist was never played before
    """

    # association information
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    """Playlist model has many-to-1 relationship with User model"""

    songs = db.relationship(
        "Song",
        cascade="delete"
    )
    """Playlist model has 1-to-many relationship with Song model"""

    def __init__(self, **kwargs):
        """
        Initializes a Playlist object
        
        kwargs:
            sum_length (int): Total sum. length of songs in playlist
            title (str): Title of playlist, "" if playlist is not favorited
            history (Datetime): Datetime when the playlist was last played, null if playlist was never played before
            user_id (int): User id that Playlist belongs to
        """
        self.sum_length = kwargs.get("sum_length")
        self.title = kwargs.get("title", "")
        self.history = kwargs.get("history")
        self.user_id = kwargs.get("user_id")


class Song(db.Model):
    """
    Song model    
    
    Has many-to-1 relationship with Playlist model
    """
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # song information
    spotify_id = db.Column(db.String, nullable=False)

    # association information
    playlist_id = db.Column(db.Integer, db.ForeignKey(
        "playlist.id"), nullable=False)
    """Song model has many-to-1 relationship with Playlist model"""

    def __init__(self, **kwargs):
        """
        Initializes a Playlist object
        
        kwargs:
            spotify_id (str) = Spotify id of song
            playlist_id (int) = Playlist that Song belongs to
        """
        self.spotify_id = kwargs.get("spotify_id")
        self.playlist_id = kwargs.get("playlist_id")
