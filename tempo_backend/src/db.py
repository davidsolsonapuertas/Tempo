import datetime
import hashlib
import os
import bcrypt
import requests
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
    """Spotify id of the user"""

    # user information
    username = db.Column(db.String, nullable=False, unique=True)
    """Username of user, same as the user's Spotify's username"""

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
            id (string): Spotify id of the user
            username (str): Username of Spotify user
        """
        self.id = kwargs.get("id")
        self.username = kwargs.get("username")

    def serialize(self):
        """
        Serialize User object, includes all object fields
        """
        return {
            "id": self.id,
            "playlists": [p.simple_serialize() for p in self.playlists]
        }


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
