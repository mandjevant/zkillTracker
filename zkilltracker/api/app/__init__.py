from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import environ
import uuid
from flask_socketio import SocketIO


db = SQLAlchemy()
app = Flask(__name__)
db_name = "zkillboard_stats.db"
app.secret_key = str(uuid.uuid4())
socketio = SocketIO(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_name
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
EVE_CLIENT_ID = environ.get("CLIENT_ID")
EVE_CLIENT_SECRET = environ.get("SECRET_KEY")
EVE_REDIRECT_URI = environ.get("CALLBACK_URL")
EVE_AUTH_URL = "https://login.eveonline.com/v2/oauth/authorize"
EVE_TOKEN_URL = "https://login.eveonline.com/v2/oauth/token"
EVE_VERIFY_URL = "https://esi.evetech.net/verify/"

db.init_app(app)

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

socketio.run(app)
