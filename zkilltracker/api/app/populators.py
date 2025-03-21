from flask import jsonify
from app import db, app
from app.models import Corporation, Months, Members
import requests
import time


def add_corp(corporation_id: int):
    try:
        url = f"https://zkillboard.com/api/stats/corporationID/{corporation_id}/"
        response = requests.get(url)
        data = response.json()

        months_data = data.get("months", {})

        for month, stats in months_data.items():
            year = int(month[:4])
            month = int(month[4:])
            entry = Months(
                corporationID=corporation_id,
                year=year,
                month=month,
                shipsLost=stats.get("shipsLost", 0),
                pointsLost=stats.get("pointsLost", 0),
                iskLost=stats.get("iskLost", 0),
                shipsDestroyed=stats.get("shipsDestroyed", 0),
                pointsDestroyed=stats.get("pointsDestroyed", 0),
                iskDestroyed=stats.get("iskDestroyed", 0),
            )
            db.session.merge(entry)

        info = data.get("info", {})
        corporation_entry = Corporation(
            id=corporation_id,
            allianceID=info.get("allianceID", 0),
            ceoID=info.get("ceoID", 0),
            dateFounded=info.get("date_founded", ""),
            memberCount=info.get("memberCount", 0),
            name=info.get("name", ""),
            taxRate=info.get("taxRate", 0),
            ticker=info.get("ticker", ""),
            soloKills=data.get("soloKills", 0),
            soloLosses=data.get("soloLosses", 0),
            avgGangSize=data.get("avgGangSize", 0.0),
            iskLost=data.get("iskLost", 0),
            attackersLost=data.get("attackersLost", 0),
            shipsDestroyed=data.get("shipsDestroyed", 0),
            iskDestroyed=data.get("iskDestroyed", 0),
            attackersDestroyed=data.get("attackersDestroyed", 0),
        )

        db.session.merge(corporation_entry)
        db.session.commit()

        return jsonify({"status": "success", "corporation_id": corporation_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def update_corp():
    with app.app_context():
        try:
            corporation_ids = db.session.query(Corporation.id).all()
            corporation_ids = [cid[0] for cid in corporation_ids]

            for corporation_id in corporation_ids:
                time.sleep(7)
                url = (
                    f"https://zkillboard.com/api/stats/corporationID/{corporation_id}/"
                )
                try:
                    response = requests.get(url)
                    data = response.json()

                    info = data.get("info", {})
                    corporation_entry = (
                        db.session.query(Corporation)
                        .filter(Corporation.id == corporation_id)
                        .first()
                    )

                    if corporation_entry:
                        corporation_entry.allianceID = info.get("allianceID", 0)
                        corporation_entry.ceoID = info.get("ceoID", 0)
                        corporation_entry.dateFounded = info.get("date_founded", "")
                        corporation_entry.memberCount = info.get("memberCount", 0)
                        corporation_entry.name = info.get("name", "")
                        corporation_entry.taxRate = info.get("taxRate", 0)
                        corporation_entry.ticker = info.get("ticker", "")
                        corporation_entry.soloKills = data.get("soloKills", 0)
                        corporation_entry.soloLosses = data.get("soloLosses", 0)
                        corporation_entry.avgGangSize = data.get("avgGangSize", 0.0)
                        corporation_entry.iskLost = data.get("iskLost", 0)
                        corporation_entry.attackersLost = data.get("attackersLost", 0)
                        corporation_entry.shipsDestroyed = data.get("shipsDestroyed", 0)
                        corporation_entry.iskDestroyed = data.get("iskDestroyed", 0)
                        corporation_entry.attackersDestroyed = data.get(
                            "attackersDestroyed", 0
                        )

                        db.session.merge(corporation_entry)

                    months_data = data.get("months", {})
                    for month, stats in months_data.items():
                        year = int(month[:4])
                        month = int(month[4:])
                        entry = Months(
                            corporationID=corporation_id,
                            year=year,
                            month=month,
                            shipsLost=stats.get("shipsLost", 0),
                            pointsLost=stats.get("pointsLost", 0),
                            iskLost=stats.get("iskLost", 0),
                            shipsDestroyed=stats.get("shipsDestroyed", 0),
                            pointsDestroyed=stats.get("pointsDestroyed", 0),
                            iskDestroyed=stats.get("iskDestroyed", 0),
                        )
                        db.session.merge(entry)
                except:
                    continue

                db.session.commit()

        except Exception as e:
            print(e)
            db.session.rollback()


def fill_members():
    try:
        corporation_ids = db.session.query(Corporation.id).all()
        for corp_id in corporation_ids:
            fill_members_corp(corporation_id=corp_id)

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def fill_members_corp(corporation_id: int):
    response = requests.get(f"https://evewho.com/api/corplist/{corporation_id}")
    data = response.json()

    all_api_chars = []
    for char in data["characters"]:
        all_api_chars.append([char["character_id"], char["name"], corporation_id])

    members_to_add = []
    members_to_update = []

    db_members = Members.query.all()
    db_members_dict = {member.character_id: member for member in db_members}

    api_char_ids = {char[0] for char in all_api_chars}

    for char_id, name, corp_id in all_api_chars:
        if char_id not in db_members_dict:
            members_to_add.append(
                Members(character_id=char_id, name=name, corporation_id=corp_id)
            )
        else:
            member = db_members_dict[char_id]
            if member.corporation_id != corp_id:
                member.corporation_id = corp_id
                members_to_update.append(member)

    for member in db_members:
        if (
            member.corporation_id == corporation_id
            and member.character_id not in api_char_ids
        ):
            member.corporation_id = None
            members_to_update.append(member)

    if members_to_add:
        db.session.bulk_save_objects(members_to_add)

    if members_to_update:
        db.session.bulk_save_objects(members_to_update)

    db.session.commit()
