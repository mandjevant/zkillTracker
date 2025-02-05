from app import EVE_CLIENT_ID, EVE_CLIENT_SECRET, login_manager, db
from app.models import ApprovedCharacters, AdminCharacters, ApprovedMembers
from flask import session, jsonify
from jose import jwt
import requests
import base64


def serialize_corporation(corp):
    return {
        "id": corp.id,
        "allianceID": corp.allianceID,
        "ceoID": corp.ceoID,
        "dateFounded": corp.dateFounded,
        "memberCount": corp.memberCount,
        "name": corp.name,
        "taxRate": corp.taxRate,
        "ticker": corp.ticker,
        "soloKills": corp.soloKills,
        "soloLosses": corp.soloLosses,
        "avgGangSize": corp.avgGangSize,
        "iskLost": corp.iskLost,
        "attackersLost": corp.attackersLost,
        "shipsDestroyed": corp.shipsDestroyed,
        "iskDestroyed": corp.iskDestroyed,
        "attackersDestroyed": corp.attackersDestroyed,
    }


def serialize_month(month):
    return {
        "corporationID": month.corporationID,
        "year": month.year,
        "month": month.month,
        "shipsLost": month.shipsLost,
        "pointsLost": month.pointsLost,
        "iskLost": month.iskLost,
        "shipsDestroyed": month.shipsDestroyed,
        "pointsDestroyed": month.pointsDestroyed,
        "iskDestroyed": month.iskDestroyed,
    }


def serialize_alliance(entry):
    return {
        "corporationTicker": entry.corporationTicker,
        "kills": entry.kills,
        "mains": entry.mains,
        "activeMains": entry.activeMains,
        "killsPerActiveMain": entry.killsPerActiveMain,
        "percentageOfAllianceKills": entry.percentageOfAllianceKills,
        "year": entry.year,
        "month": entry.month,
    }


def serialize_aggregations(aggs):
    return {
        "year_month": aggs.year_month,
        "totalValue": aggs.totalValue,
        "points": aggs.points,
        "npc": aggs.npc,
        "solo": aggs.solo,
        "awox": aggs.awox,
        "killCount": aggs.killCount,
    }


def serialize_member(member):
    return {
        "characterID": member.characterID,
        "characterName": member.characterName,
        "corporationID": member.corporationID,
    }


def serialize_member_kills(member_kill):
    return {
        "killID": member_kill.killID,
        "attackerCharacterID": member_kill.characterID,
        "damageDone": member_kill.damageDone,
        "finalBlow": member_kill.finalBlow,
        "attackerShipTypeID": member_kill.shipTypeID,
    }


def serialize_kills(kill):
    return {
        "killID": kill.killID,
        "locationID": kill.locationID,
        "totalValue": kill.totalValue,
        "points": kill.points,
        "npc": kill.npc,
        "solo": kill.solo,
        "awox": kill.awox,
        "datetime": kill.datetime,
        "shipTypeID": kill.shipTypeID,
    }


def serialize_items(item):
    return {
        "type_id": item.type_id,
        "name": item.name,
    }


def serialize_month_progress(item):
    return {
        "characterName": item.characterName,
        "kills": item.kills,
    }


@login_manager.user_loader
def load_user(id):
    ceo2ic = ApprovedCharacters.query.filter_by(id=id).first()
    if ceo2ic is not None:
        return ceo2ic
    else:
        return ApprovedMembers.query.filter_by(id=id).first()


def is_admin(user):
    return AdminCharacters.query.filter_by(id=user.id).first() is not None


def is_member(user):
    return ApprovedMembers.query.filter_by(id=user.id).first() is not None


def _validate_eve_jwt(token: str) -> dict:
    res = requests.get(
        "https://login.eveonline.com/.well-known/oauth-authorization-server"
    )
    res.raise_for_status()
    data = res.json()

    try:
        jwks_uri = data["jwks_uri"]
    except KeyError:
        raise RuntimeError(
            f"Invalid data received from the SSO meta data endpoint: {data}"
        )

    res = requests.get(jwks_uri)
    res.raise_for_status()
    data = res.json()

    try:
        jwk_sets = data["keys"]
    except KeyError:
        raise RuntimeError(f"Invalid data received from the the jwks endpoint: {data}")

    jwk_set = [item for item in jwk_sets if item["alg"] == "RS256"].pop()

    contents = jwt.decode(
        token=token,
        key=jwk_set,
        algorithms=jwk_set["alg"],
        issuer=("login.eveonline.com", "https://login.eveonline.com"),
        audience="EVE Online",
    )
    return contents


def get_payload(authorization_code: str):
    payload = {"grant_type": "authorization_code", "code": authorization_code}

    credentials = f"{EVE_CLIENT_ID}:{EVE_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "login.eveonline.com",
    }

    url = "https://login.eveonline.com/v2/oauth/token"
    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        access_token = response.json()["access_token"]
    else:
        raise RuntimeError("Could not get access_token")

    content = _validate_eve_jwt(access_token)
    character_id = content["sub"][14:]
    character_name = content["name"]

    session["character_id"] = character_id
    session["character_name"] = character_name

    return character_id


def check_user_status():
    character_id = session.get("character_id")
    character_name = session.get("character_name")
    if not character_id:
        return jsonify({"status": "in_progress"})

    approved_character = ApprovedCharacters.query.filter_by(id=character_id).first()
    approved_member = ApprovedMembers.query.filter_by(id=character_id).first()

    if approved_character:
        admin_character = AdminCharacters.query.filter_by(id=character_id).first()
        return {
            "status": "Done",
            "is_member": False,
            "logged_in": True,
            "is_admin": bool(admin_character),
            "character_name": character_name,
        }
    elif approved_member:
        return {
            "status": "Done",
            "is_member": True,
            "logged_in": True,
            "is_admin": False,
            "character_name": character_name,
        }
    else:
        return {
            "status": "False",
            "is_member": False,
            "logged_in": False,
            "is_admin": False,
            "character_name": None,
        }
