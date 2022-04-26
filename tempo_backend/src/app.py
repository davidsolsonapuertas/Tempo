import json
from turtle import update

from db import db
from flask import Flask, request
import users_dao
import datetime

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
@app.route("/", methods=["GET"])
def cry():
    """
    Cry
    """
    pass


@app.route("/", methods=["POST"])
def cry_more():
    """
    Cry more
    """
    pass


# ------------- RUN APP -------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
