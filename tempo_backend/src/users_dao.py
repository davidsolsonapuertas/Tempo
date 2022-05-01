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
    return User.query.filter(User.username == username).first()


def get_user_by_session_token(session_token):
    """
    Returns a user object from the database given a session token
    """
    return User.query.filter(User.session_token == session_token).first()


def get_user_by_update_token(update_token):
    """
    Returns a user object from the database given an update token
    """
    return User.query.filter(User.update_token == update_token).first()


def renew_session(update_token):
    """
    Renews a user's session token

    Returns the User object
    """
    user = get_user_by_update_token(update_token)

    if user is None:
        raise Exception("Invalid update token")
    
    user.renew_session()
    db.session.commit()

    return user

def create_user(username):
    """
    Creates a User object in the database

    If the creation was successful, User object is added to the database
    """

    potential_user=get_user_by_username(username)

    #If a user already exists
    if potential_user is not None:
        return False, potential_user

    user=User(username=username)
    db.session.add(user)
    db.session.commit()
    return True, user