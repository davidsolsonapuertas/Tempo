import datetime
import hashlib
import os
import bcrypt

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ------------- TABLES -------------

class User(db.Model):
    """
    User model
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User information
    username = db.Column(db.String, nullable=False, unique=True)
    
    def __init__(self, **kwargs):
        """
        Initializes a User object
        """
        self.username = kwargs.get("username")
        self.renew_session()
    
    def renew_session(self):
        """
        Calls on renew_session of associated session token
        """
        pass

    def verify_session_token(self, session_token):
        """
        Calls on verify_session_token of associated session token 
        """
        pass

class Token(db.Model):
    """
    Token model
    """
    __tablename__ = 'tokens'
    
    def __init__(self, **kwargs):
        """
        Initializes a Token object
        """
        pass
    
    def renew_session(self):
        """
        Renews session of a user
        """
        pass
    
    def verify_password(self, password):
        """
        Verifies the password of a user
        """
        pass
    
    def verify_session_token(self, session_token):
        """
        Verifies the session token of a user
        """
        pass

    def verify_update_token(self, update_token):
        """
        Verifies the update token of a user
        """
        pass
    
class Playlist(db.Model):
    """
    Playlist model
    """
    __tablename__ = 'playlists'
    
    def __init__(self, **kwargs):
        """
        Initializes a Playlist object
        """
        pass

