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


def renew_session(update_token):
    """
    Renews a user's session token

    Returns the User object
    """
    pass
