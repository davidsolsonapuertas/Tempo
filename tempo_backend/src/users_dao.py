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


def get_user_by_id(id):
    """
    Returns a user object from the database given an id
    """
    return User.query.filter(User.id == id).first()


def create_user(id, username):
    """
    Creates a User object in the database

    If the creation was successful, User object is added to the database
    """

    potential_user = get_user_by_id(id)

    # If a user already exists
    if potential_user is not None:
        return False, potential_user

    user = User(id=id, username=username)
    db.session.add(user)
    db.session.commit()
    return True, user
