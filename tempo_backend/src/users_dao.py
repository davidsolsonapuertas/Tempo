"""
DAO (Data Access Object) file

Helper file containing functions for accessing data in our database
"""

from db import User
from db import db


def get_user_by_username(username):
    """
    Returns a user object from the database given an username
    """
    pass


def get_user_by_session_token(session_token):
    """
    Returns a user object from the database given a session token
    """
    pass


def get_user_by_update_token(update_token):
    """
    Returns a user object from the database given an update token
    """
    pass


def verify_credentials(username, password):
    """
    Returns true if the credentials match, otherwise returns false
    """
    pass


def create_user(username, password):
    """
    Creates a User object in the database

    Returns if creation was successful, and the User object
    """
    pass


def renew_session(update_token):
    """
    Renews a user's session token

    Returns the User object
    """
    pass
