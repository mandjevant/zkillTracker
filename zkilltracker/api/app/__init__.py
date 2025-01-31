from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
import flask_login
import uuid
import os


db = SQLAlchemy()
app = Flask(__name__)
CORS(app, supports_credentials=True)
db_name = "zkillboard_stats.db"
app.secret_key = str(uuid.uuid4())
login_manager = flask_login.LoginManager()
UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_name}?check_same_thread=False"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
EVE_CLIENT_ID = environ.get("CLIENT_ID")
EVE_CLIENT_SECRET = environ.get("SECRET_KEY")
EVE_REDIRECT_URI = environ.get("CALLBACK_URL")
OWNER_CHAR_ID = environ.get("OWNER_CHAR_ID")
EVE_AUTH_URL = "https://login.eveonline.com/v2/oauth/authorize"
EVE_TOKEN_URL = "https://login.eveonline.com/v2/oauth/token"
EVE_VERIFY_URL = "https://esi.evetech.net/verify/"

db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    from app.models import (
        Corporation,
        Months,
        Alliance,
        MemberKills,
        Members,
        Kills,
        AdminCharacters,
        ApprovedCharacters,
    )

    db.create_all()


from app import routes
