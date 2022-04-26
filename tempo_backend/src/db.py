from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ------------- TABLES -------------

class User(db.Model):
    __tablename__ = 'users'


class Playlist(db.Model):
    __tablename__ = 'playlists'


class Token(db.Model):
    __tablename__ = 'tokens'
