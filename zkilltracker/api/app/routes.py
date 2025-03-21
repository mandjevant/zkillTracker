from flask import jsonify, request, redirect, session
from app import (
    app,
    db,
    EVE_AUTH_URL,
    EVE_REDIRECT_URI,
    EVE_CLIENT_ID,
    OWNER_CHAR_ID,
)
from app.models import (
    Months,
    Corporation,
    Alliance,
    Members,
    Kills,
    MemberKills,
    Items,
    ApprovedCharacters,
    AdminCharacters,
    ApprovedMembers,
)
from app.helpers import (
    serialize_corporation,
    serialize_month,
    serialize_alliance,
    serialize_alliance_parameterized,
    serialize_aggregations,
    serialize_aggregations_parameterized,
    serialize_member,
    serialize_kills,
    serialize_member_kills,
    serialize_items,
    serialize_month_progress,
    serialize_alliance_tab,
    get_payload,
    check_user_status,
    load_user,
    is_admin,
    is_member,
)
from app.taskmanager import KillRefreshTask, MemberRefreshTask
from app.populators import add_corp, update_corp
from app.decorators import login_required, admin_required
from flask_login import login_user, logout_user, current_user
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dateutil.relativedelta import relativedelta
from werkzeug.utils import secure_filename
from sqlalchemy import func, extract, String, text
import pandas as pd
import threading
import datetime
import logging
import sqlite3
import atexit
import uuid
import os


logging.basicConfig(level=logging.DEBUG)


scheduler = BackgroundScheduler()
kill_trigger = CronTrigger(
    year="*", month="*", day="*", hour="6", minute="0", second="0"
)
scheduler.add_job(KillRefreshTask(uuid.uuid4).get_kills, kill_trigger)
kill_trigger_two = CronTrigger(
    year="*", month="*", day="*", hour="18", minute="0", second="0"
)
scheduler.add_job(KillRefreshTask(uuid.uuid4).get_kills, kill_trigger_two)
corp_trigger = CronTrigger(
    year="*", month="*", day="*", hour="9", minute="30", second="0"
)
scheduler.add_job(update_corp, corp_trigger)
corp_trigger_two = CronTrigger(
    year="*", month="*", day="*", hour="21", minute="30", second="0"
)
scheduler.add_job(update_corp, corp_trigger_two)
scheduler.start()


atexit.register(lambda: scheduler.shutdown())


@app.route("/login", methods=["GET"])
def login():
    auth_url = f"{EVE_AUTH_URL}?response_type=code&state={uuid.uuid4()}&redirect_uri={EVE_REDIRECT_URI}&client_id={EVE_CLIENT_ID}"
    return auth_url


@app.route("/oauth-callback/", methods=["GET", "POST"])
def oauth_callback():
    auth_code = request.args.get("code")
    if auth_code:
        character_id = get_payload(auth_code)
        user = load_user(id=character_id)

        user_status = check_user_status()
        logging.debug(f"Login: user_status={user_status}")

        if user:
            login_user(user)
            return redirect("https://zkilltracker.mostlycapstable.com/corporation"), 200

    return redirect("https://zkilltracker.mostlycapstable.com/corporation"), 200


@app.route("/login_status")
def login_status():
    if current_user.is_authenticated:
        is_admin_user = is_admin(current_user)
        is_member_user = is_member(current_user)
        return jsonify(
            {
                "isLoggedIn": True,
                "isAdmin": is_admin_user,
                "isMember": is_member_user,
                "characterName": session["character_name"],
            }
        )
    else:
        return jsonify(
            {
                "isLoggedIn": False,
                "isAdmin": False,
                "isMember": False,
                "character_name": "",
            }
        )


@app.route("/logout")
@login_required
def logout():
    session.pop("character_id", None)
    session.pop("character_name", None)
    logout_user()

    logging.debug(f'Logout: character_id={session.get("character_id")}')
    return jsonify(
        {"isLoggedIn": False, "isAdmin": False, "isMember": False, "character_name": ""}
    )


@app.route("/corporation/<int:corporation_id>/months", methods=["GET"])
@login_required
def get_months_corporation(corporation_id: int):
    months = (
        db.session.query(Months)
        .filter_by(corporationID=corporation_id)
        .order_by(Months.year, Months.month)
        .all()
    )
    if not months:
        return jsonify({"error": "Corporation not found"}), 404

    return jsonify([serialize_month(month) for month in months])


@app.route("/corporation/<int:corporation_id>", methods=["GET"])
@login_required
def get_corporation(corporation_id: int):
    corporation = db.session.query(Corporation).filter_by(id=corporation_id).first()
    if corporation is None:
        return jsonify({"error": "Corporation not found"}), 404

    return jsonify(serialize_corporation(corporation))


@app.route("/corporations", methods=["GET"])
@login_required
def get_all_corporations():
    corporations = (
        db.session.query(Corporation).filter(Corporation.allianceID == 99011223).all()
    )

    return jsonify([serialize_corporation(corp) for corp in corporations])


@app.route("/get_alliance_data", methods=["GET"])
@login_required
def get_alliance_data():
    start_year = int(request.args.get("start_year"))
    start_month = int(request.args.get("start_month"))
    end_year = int(request.args.get("end_year"))
    end_month = int(request.args.get("end_month"))
    corporations = request.args.getlist("corporations")

    query = db.session.query(Alliance).filter(
        (Alliance.year > start_year)
        | ((Alliance.year == start_year) & (Alliance.month >= start_month)),
        (Alliance.year < end_year)
        | ((Alliance.year == end_year) & (Alliance.month <= end_month)),
    )

    result = query.filter(Alliance.corporationTicker.in_(corporations)).all()
    serialized_result = [serialize_alliance(entry) for entry in result]

    serialized_result.sort(key=lambda x: (x["year"], x["month"]))

    previous_mains = {ticker: None for ticker in corporations}

    for entry in serialized_result:
        corporation_ticker = entry["corporationTicker"]
        current_mains = entry["mains"]

        if previous_mains[corporation_ticker] is None:
            entry["growthRate"] = 1  # No previous month data
        else:
            prev_mains = previous_mains[corporation_ticker]
            entry["growthRate"] = current_mains / prev_mains if prev_mains > 0 else 1

        previous_mains[corporation_ticker] = current_mains

    return jsonify(serialized_result)


@app.route("/get_alliance_tickers", methods=["GET"])
@login_required
def get_alliance_tickers():
    start_year = int(request.args.get("start_year"))
    start_month = int(request.args.get("start_month"))
    end_year = int(request.args.get("end_year"))
    end_month = int(request.args.get("end_month"))

    results = (
        db.session.query(Alliance)
        .filter(
            (Alliance.year > start_year)
            | ((Alliance.year == start_year) & (Alliance.month >= start_month)),
            (Alliance.year < end_year)
            | ((Alliance.year == end_year) & (Alliance.month <= end_month)),
        )
        .all()
    )

    return jsonify([serialize_alliance(entry) for entry in results])


@app.route("/corporation/<int:corporation_id>/members", methods=["GET"])
@login_required
def get_corporation_members(corporation_id: int):
    members = (
        db.session.query(Members).filter(Members.corporationID == corporation_id).all()
    )

    if not members:
        return jsonify({"error": "Corporation not found or has no members"}), 404

    return jsonify([serialize_member(member) for member in members])


@app.route("/corporation/<int:corporation_id>/deadbeats", methods=["GET"])
@login_required
def get_corporation_deadbeats(corporation_id: int):
    try:
        now = datetime.datetime.utcnow()
        six_months_ago = now - datetime.timedelta(days=180)
        two_months_ago = now - datetime.timedelta(days=60)

        recent_killers_subquery = (
            db.session.query(MemberKills.characterID)
            .join(Kills, Kills.killID == MemberKills.killID)
            .filter(
                Kills.datetime >= two_months_ago,
                MemberKills.characterID.in_(
                    db.session.query(Members.characterID).filter(
                        Members.corporationID == corporation_id
                    )
                ),
            )
            .distinct()
        )

        deadbeats_query = (
            db.session.query(Members.characterID, Members.characterName)
            .outerjoin(MemberKills, Members.characterID == MemberKills.characterID)
            .join(Kills, Kills.killID == MemberKills.killID)
            .filter(
                Members.corporationID == corporation_id,
                ~Members.characterID.in_(recent_killers_subquery),
                Kills.datetime >= six_months_ago,
            )
            .distinct()
            .all()
        )

        deadbeats_list = [
            {"characterID": member.characterID, "characterName": member.characterName}
            for member in deadbeats_query
        ]
        return jsonify({"deadbeats": deadbeats_list}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/corporation/add/<int:corporation_id>", methods=["POST"])
@login_required
@admin_required
def add_corporation(corporation_id: int):
    existing_corporation = (
        db.session.query(Corporation).filter_by(id=corporation_id).first()
    )

    if existing_corporation:
        return jsonify({"error": "Corporation already exists"}), 400

    return add_corp(corporation_id)


@app.route("/member/<int:character_id>/monthlyaggregations", methods=["GET"])
@login_required
def get_member_monthly_aggregations(character_id: int):
    date_range = (
        db.session.query(
            func.min(func.strftime("%Y-%m", Kills.datetime)).label("min_date"),
            func.max(func.strftime("%Y-%m", Kills.datetime)).label("max_date"),
        )
        .join(MemberKills, MemberKills.killID == Kills.killID)
        .filter(MemberKills.characterID == character_id)
        .first()
    )

    if not date_range.min_date or not date_range.max_date:
        return jsonify([])

    start_date = datetime.datetime.strptime(date_range.min_date, "%Y-%m")
    end_date = datetime.datetime.strptime(date_range.max_date, "%Y-%m")

    year_months = []
    current_date = start_date
    while current_date <= end_date:
        year_months.append(current_date.strftime("%Y-%m"))
        current_date += relativedelta(months=1)

    results = (
        db.session.query(
            func.strftime("%Y-%m", Kills.datetime).label("year_month"),
            func.sum(Kills.totalValue).label("totalValue"),
            func.sum(Kills.points).label("points"),
            func.sum(Kills.npc).label("npc"),
            func.sum(Kills.solo).label("solo"),
            func.sum(Kills.awox).label("awox"),
            func.count().label("killCount"),
        )
        .select_from(MemberKills)
        .join(Kills, MemberKills.killID == Kills.killID)
        .filter(MemberKills.characterID == character_id)
        .group_by(func.strftime("%Y-%m", Kills.datetime))
        .all()
    )

    results_dict = {
        result.year_month: serialize_aggregations(result) for result in results
    }

    aggregated_results = []
    for ym in year_months:
        if ym in results_dict:
            aggregated_results.append(results_dict[ym])
        else:
            aggregated_results.append(
                {
                    "year_month": ym,
                    "totalValue": 0,
                    "points": 0,
                    "npc": 0,
                    "solo": 0,
                    "awox": 0,
                    "killCount": 0,
                }
            )

    return jsonify(aggregated_results)


@app.route("/member/<int:character_id>/aggregations", methods=["GET"])
@login_required
def get_member_aggregations(character_id: int):
    date_range = (
        db.session.query(
            func.min(func.strftime("%Y-%m", Kills.datetime)).label("min_date"),
            func.max(func.strftime("%Y-%m", Kills.datetime)).label("max_date"),
        )
        .join(MemberKills, MemberKills.killID == Kills.killID)
        .filter(MemberKills.characterID == character_id)
        .first()
    )

    if not date_range.min_date or not date_range.max_date:
        return jsonify([])

    start_date = datetime.datetime.strptime(date_range.min_date, "%Y-%m")
    end_date = datetime.datetime.strptime(date_range.max_date, "%Y-%m")

    year_months = []
    current_date = start_date
    while current_date <= end_date:
        year_months.append(current_date.strftime("%Y-%m"))
        current_date += relativedelta(months=1)

    results = (
        db.session.query(
            func.strftime("%Y-%m", Kills.datetime).label("year_month"),
            func.sum(Kills.totalValue).label("totalValue"),
            func.sum(Kills.points).label("points"),
            func.sum(Kills.npc).label("npc"),
            func.sum(Kills.solo).label("solo"),
            func.sum(Kills.awox).label("awox"),
            func.count().label("killCount"),
        )
        .select_from(MemberKills)
        .join(Kills, MemberKills.killID == Kills.killID)
        .filter(MemberKills.characterID == character_id)
        .group_by(func.strftime("%Y-%m", Kills.datetime))
        .all()
    )

    results_dict = {
        result.year_month: serialize_aggregations(result) for result in results
    }

    aggregated_results = []
    for ym in year_months:
        if ym in results_dict:
            aggregated_results.append(results_dict[ym])
        else:
            aggregated_results.append(
                {
                    "year_month": ym,
                    "totalValue": 0,
                    "points": 0,
                    "npc": 0,
                    "solo": 0,
                    "awox": 0,
                    "killCount": 0,
                }
            )

    return jsonify(aggregated_results)


@app.route("/member/<int:character_id>/kills/all", methods=["GET"])
@login_required
def get_all_member_kills(character_id: int):
    kills = (
        db.session.query(MemberKills, Kills)
        .select_from(MemberKills)
        .join(Kills, MemberKills.killID == Kills.killID)
        .filter(MemberKills.characterID == character_id)
        .all()
    )

    if not kills:
        return jsonify({"error": "No kills found for the specified member"}), 404

    serialized_results = [
        {**serialize_member_kills(mk), **serialize_kills(k)} for mk, k in kills
    ]

    return jsonify(serialized_results)


@app.route(
    "/member/<int:character_id>/kills/year/<int:year_id>/month/<int:month_id>",
    methods=["GET"],
)
@login_required
def get_month_member_kills(character_id: int, year_id: int, month_id: int):
    kills = (
        db.session.query(MemberKills, Kills)
        .select_from(MemberKills)
        .join(Kills, MemberKills.killID == Kills.killID)
        .filter(
            MemberKills.characterID == character_id,
            extract("year", Kills.datetime) == year_id,
            extract("month", Kills.datetime) == month_id,
        )
        .all()
    )

    if not kills:
        return (
            jsonify(
                {"error": "No kills found for the specified member in the given month"}
            ),
            404,
        )

    serialized_results = [
        {**serialize_member_kills(mk), **serialize_kills(k)} for mk, k in kills
    ]

    return jsonify(serialized_results)


@app.route(
    "/corporation/<int:corporation_id>/kills/year/<int:year_id>/month/<int:month_id>",
    methods=["GET"],
)
@login_required
def get_month_corporation_kills(corporation_id: int, year_id: int, month_id: int):
    kills = (
        db.session.query(Members.characterName, func.count(Kills.killID).label("kills"))
        .join(MemberKills, Members.characterID == MemberKills.characterID)
        .join(Kills, MemberKills.killID == Kills.killID)
        .filter(
            Members.corporationID == corporation_id,
            extract("year", Kills.datetime) == year_id,
            extract("month", Kills.datetime) == month_id,
        )
        .group_by(Members.characterID)
        .order_by(func.count(Kills.killID).desc())
        .all()
    )

    if not kills:
        return (
            jsonify(
                {
                    "error": "No kills found for the specified corporation in the given month"
                }
            ),
            404,
        )

    return jsonify([serialize_month_progress(kill) for kill in kills])


@app.route(
    "/corporation/<int:corporation_id>/low_kills/year/<int:year_id>/month/<int:month_id>",
    methods=["GET"],
)
@login_required
def get_low_kills(corporation_id: int, year_id: int, month_id: int):
    subquery = (
        db.session.query(
            MemberKills.characterID, func.count(Kills.killID).label("kills")
        )
        .join(Kills, MemberKills.killID == Kills.killID)
        .filter(
            extract("year", Kills.datetime) == year_id,
            extract("month", Kills.datetime) == month_id,
        )
        .group_by(MemberKills.characterID)
        .subquery()
    )

    members_with_low_kills = (
        db.session.query(
            Members.characterName,
            func.coalesce(subquery.c.kills, 0).label("kills"),
        )
        .outerjoin(subquery, Members.characterID == subquery.c.characterID)
        .filter(
            Members.corporationID == corporation_id,
            (subquery.c.kills == None) | (subquery.c.kills < 10),
        )
        .order_by(func.coalesce(subquery.c.kills, 0).desc())
        .all()
    )

    if not members_with_low_kills:
        return (
            jsonify(
                {
                    "error": "No members found with less than 10 kills or zero kills for the specified corporation in the given month"
                }
            ),
            404,
        )

    return jsonify(
        [serialize_month_progress(member) for member in members_with_low_kills]
    )


@app.route(
    "/member/<int:character_id>/change_corporation/<int:corporation_id>",
    methods=["PUT"],
)
@login_required
@admin_required
def change_member_corporation(character_id: int, corporation_id: int):
    corporation = db.session.query(Corporation).filter_by(id=corporation_id).first()
    if corporation is None:
        return jsonify({"error": "Corporation not found"}), 404

    member = db.session.query(Members).filter_by(characterID=character_id).first()
    if member is None:
        return jsonify({"error": "Member not found"}), 404

    member.corporationID = corporation_id
    db.session.commit()

    return jsonify({"message": "Corporation updated successfully"})


@app.route(
    "/corporation/<int:corporation_id>/change_alliance/<int:alliance_id>",
    methods=["PUT"],
)
@login_required
@admin_required
def change_corporation_alliance(corporation_id: int, alliance_id: int):
    corporation = db.session.query(Corporation).filter_by(id=corporation_id).first()
    if corporation is None:
        return jsonify({"error": "Corporation not found"}), 404

    corporation.allianceID = alliance_id
    db.session.commit()

    return jsonify({"message": "Corporation updated successfully"})


@app.route(
    "/members/add/<int:character_id>/<string:character_name>/<int:corporation_id>",
    methods=["POST"],
)
@login_required
@admin_required
def add_member(character_id: int, character_name: str, corporation_id: int):
    corporation = db.session.query(Corporation).filter_by(id=corporation_id).first()
    if corporation is None:
        return jsonify({"error": "Corporation not found"}), 404

    existing_member = (
        db.session.query(Members).filter_by(characterID=character_id).first()
    )
    if existing_member is not None:
        return jsonify({"error": "Member already exists"}), 400

    new_member = Members(
        characterID=character_id,
        characterName=character_name,
        corporationID=corporation_id,
    )
    db.session.add(new_member)
    db.session.commit()

    return jsonify({"message": "Member added successfully"})


@app.route("/kills/add", methods=["GET"])
@login_required
@admin_required
def add_kills():
    uniq_id = uuid.uuid4()
    newTask = KillRefreshTask(run_id=uniq_id)
    threading.Thread(target=newTask.get_kills).start()

    return jsonify({"task_id": uniq_id})


@app.route("/members/add", methods=["GET"])
@login_required
@admin_required
def add_members():
    uniq_id = uuid.uuid4()
    newTask = MemberRefreshTask(run_id=uniq_id)
    threading.Thread(target=newTask.fill_members).start()

    return jsonify({"task_id": uniq_id})


@app.route("/corporations/refresh", methods=["GET"])
@login_required
@admin_required
def refresh_corporations():
    uniq_id = uuid.uuid4()
    threading.Thread(target=update_corp).start()

    return jsonify({"task_id": uniq_id})


@app.route("/items", methods=["GET"])
def get_items():
    all_items = db.session.query(Items).all()
    return jsonify([serialize_items(item) for item in all_items])


@app.route(
    "/approved_member/add/<int:character_id>",
    methods=["POST"],
)
@login_required
@admin_required
def add_approved_member(character_id: int):
    existing_approved_member = (
        db.session.query(ApprovedMembers).filter_by(id=character_id).first()
    )
    if existing_approved_member is not None:
        return jsonify({"error": "Approved member already exists"}), 400

    new_approved = ApprovedMembers(id=character_id)
    db.session.add(new_approved)
    db.session.commit()

    return jsonify({"message": "Approved member added successfully"})


@app.route(
    "/approved_member/remove/<int:character_id>",
    methods=["POST"],
)
@login_required
@admin_required
def remove_approved_member(character_id: int):
    if character_id == int(OWNER_CHAR_ID):
        return jsonify({"error": "Not allowed to remove owner approved character"}), 400

    existing_approved_member = (
        db.session.query(ApprovedMembers).filter_by(id=character_id).first()
    )
    if existing_approved_member is None:
        return jsonify({"error": "Approved member does not exists"}), 400

    db.session.delete(existing_approved_member)
    db.session.commit()

    return jsonify({"message": "Approved member removed successfully"})


@app.route(
    "/approved/add/<int:character_id>",
    methods=["POST"],
)
@login_required
@admin_required
def add_approved(character_id: int):
    existing_approved = (
        db.session.query(ApprovedCharacters).filter_by(id=character_id).first()
    )
    if existing_approved is not None:
        return jsonify({"error": "Approved character already exists"}), 400

    new_approved = ApprovedCharacters(id=character_id)
    db.session.add(new_approved)
    db.session.commit()

    return jsonify({"message": "Approved character added successfully"})


@app.route(
    "/approved/remove/<int:character_id>",
    methods=["POST"],
)
@login_required
@admin_required
def remove_approved(character_id: int):
    if character_id == int(OWNER_CHAR_ID):
        return jsonify({"error": "Not allowed to remove owner approved character"}), 400

    existing_approved = (
        db.session.query(ApprovedCharacters).filter_by(id=character_id).first()
    )
    if existing_approved is None:
        return jsonify({"error": "Approved character does not exists"}), 400

    db.session.delete(existing_approved)
    db.session.commit()

    return jsonify({"message": "Approved character removed successfully"})


@app.route(
    "/admin/add/<int:character_id>",
    methods=["POST"],
)
@login_required
@admin_required
def add_admin(character_id: int):
    existing_admin = (
        db.session.query(AdminCharacters).filter_by(id=character_id).first()
    )
    if existing_admin is not None:
        return jsonify({"error": "Admin character already exists"}), 400

    new_admin = AdminCharacters(id=character_id)
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({"message": "Admin character added successfully"})


@app.route(
    "/admin/remove/<int:character_id>",
    methods=["POST"],
)
@login_required
@admin_required
def remove_admin(character_id: int):
    if character_id == int(OWNER_CHAR_ID):
        return jsonify({"error": "Not allowed to remove owner admin character"}), 400

    existing_admin = (
        db.session.query(AdminCharacters).filter_by(id=character_id).first()
    )
    if existing_admin is None:
        return jsonify({"error": "Admin character does not exists"}), 400

    db.session.delete(existing_admin)
    db.session.commit()

    return jsonify({"message": "Admin character removed successfully"})


@app.route("/upload_file", methods=["POST"])
@login_required
@admin_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith(".xlsx"):
        return jsonify({"error": "File must be .xlsx"}), 400

    try:
        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"], secure_filename(file.filename)
        )
        file.save(file_path)

        df = pd.read_excel(file_path, header=0)
        conn = sqlite3.connect("instance/zkillboard_stats.db")
        df.to_sql("alliance", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

        return jsonify({"message": "CSV processed and data stored successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/corporation/<int:corporation_id>/snapshot", methods=["GET"])
@login_required
def get_kills_per_month(corporation_id: int):
    try:
        now = datetime.datetime.utcnow()
        six_months_ago = now.replace(day=1, hour=0, minute=0, second=0) - relativedelta(
            months=6
        )
        months_list = [
            (now - relativedelta(months=i)).strftime("%Y-%m") for i in range(5, -1, -1)
        ]

        kills_query = (
            db.session.query(
                Members.characterID,
                Members.characterName,
                func.strftime("%Y-%m", Kills.datetime).label("month"),
                func.count(Kills.killID).label("kill_count"),
            )
            .join(MemberKills, Members.characterID == MemberKills.characterID)
            .join(Kills, Kills.killID == MemberKills.killID)
            .filter(
                Members.corporationID == corporation_id,
                Kills.datetime >= six_months_ago,
            )
            .group_by(Members.characterID, Members.characterName, "month")
            .all()
        )

        kills_data = {}
        for characterID, characterName, month, kill_count in kills_query:
            if characterID not in kills_data:
                kills_data[characterID] = {
                    "characterName": characterName,
                    "kills": {month: 0 for month in months_list},
                }
            kills_data[characterID]["kills"][month] = kill_count

        for member_data in kills_data.values():
            for month in months_list:
                member_data["kills"].setdefault(month, 0)
            member_data["kills"] = [
                member_data["kills"][month] for month in months_list
            ]

        result = [
            {
                "characterID": characterID,
                "characterName": member_data["characterName"],
                "kills": member_data["kills"],
                "totalKills": sum(member_data["kills"]),
            }
            for characterID, member_data in kills_data.items()
        ]
        result.sort(key=lambda x: x["totalKills"], reverse=True)

        return jsonify({"killsPerMonth": result}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/members/<string:displayOption>/stats", methods=["GET"])
@login_required
def get_members_monthly_aggregations(displayOption: str):
    match displayOption:
        case "killCount":
            select = func.count().label("killCount")
        case "totalValue":
            select = func.sum(Kills.totalValue).label("totalValue")
        case "solo":
            select = func.sum(Kills.solo).label("solo")
        case "awox":
            select = func.sum(Kills.awox).label("awox")
        case "npc":
            select = func.sum(Kills.npc).label("npc")
        case "points":
            select = func.sum(Kills.points).label("points")
        case _:
            select = func.count().label("killCount")

    members = request.args.getlist("members", type=int)
    if not members:
        return jsonify([])

    now = datetime.datetime.utcnow()
    twelve_months_ago = now.replace(day=1, hour=0, minute=0, second=0) - relativedelta(
        months=12
    )

    year_months = [
        (now - relativedelta(months=i)).strftime("%Y-%m") for i in range(11, -1, -1)
    ]

    results = (
        db.session.query(
            MemberKills.characterID,
            func.strftime("%Y-%m", Kills.datetime).label("year_month"),
            select
        )
        .select_from(MemberKills)
        .join(Kills, MemberKills.killID == Kills.killID)
        .filter(MemberKills.characterID.in_(members), Kills.datetime >= twelve_months_ago)
        .group_by(MemberKills.characterID, func.strftime("%Y-%m", Kills.datetime))
        .all()
    )

    results_dict = {}
    for result in results:
        if result.characterID not in results_dict:
            results_dict[result.characterID] = {}
        results_dict[result.characterID][result.year_month] = serialize_aggregations_parameterized(result, displayOption)

    aggregated_results = {}
    for member in members:
        aggregated_results[member] = []
        for ym in year_months:
            if ym in results_dict.get(member, {}):
                aggregated_results[member].append(results_dict[member][ym])
            else:
                aggregated_results[member].append(
                    {
                        "year_month": ym,
                        displayOption: 0,
                    }
                )

    return jsonify(aggregated_results)


@app.route("/alliance/lastmonth", methods=["GET"])
@admin_required
@login_required
def alliance_export_month():
    now = datetime.datetime.utcnow()
    last_month = now - relativedelta(months=1)

    result = db.session.query(
        Alliance.corporationTicker, 
        Alliance.kills, 
        Alliance.mains, 
        Alliance.activeMains, 
        Alliance.killsPerActiveMain, 
        Alliance.percentageOfAllianceKills
        ).filter(
        (Alliance.year == last_month.year) & (Alliance.month == last_month.month)
    ).all()

    serialized_result = [serialize_alliance_tab(entry) for entry in result]

    return jsonify(serialized_result)


@app.route("/alliance/<string:displayOption>/sixmonths", methods=["GET"])
@admin_required
@login_required
def alliance_export_sixmonths(displayOption: str):
    # match case beats eval
    match displayOption:
        case "kills":
            select = Alliance.kills
        case "mains":
            select = Alliance.mains
        case "activeMains":
            select = Alliance.activeMains
        case "killsPerActiveMain":
            select = Alliance.killsPerActiveMain
        case "percentageOfAllianceKills":
            select = Alliance.percentageOfAllianceKills
        case _:
            select = Alliance.kills
    
    now = datetime.datetime.utcnow()
    year_months = [
        (now - relativedelta(months=i)).strftime("%Y-%m") for i in range(5, -1, -1)
    ]
    
    expr = None
    for i in year_months:
        if expr is None:
            expr = ((Alliance.year == int(i[:4])) & (Alliance.month == int(i[-2:])))
        else:
            expr = expr | ((Alliance.year == int(i[:4])) & (Alliance.month == int(i[-2:])))

    results = (
        db.session.query(
            Alliance.corporationTicker,
            Alliance.year,
            Alliance.month,
            select
        )
        .filter(expr)
        .all()
    )

    serialized_results = [serialize_alliance_parameterized(entry, displayOption) for entry in results]
    keys = list(set([v for i in serialized_results for k, v in i.items() if k == "corporationTicker"]))

    result = {key: [0] * 6 for key in keys}
    year_month_index = {ym: i for i, ym in enumerate(year_months)}
    for entry in serialized_results:
        ym = f"{entry['year']}-{str(entry['month']).zfill(2)}"
        if ym in year_month_index:
            index = year_month_index[ym]
            result[entry["corporationTicker"]][index] = entry[displayOption]

    return jsonify(result)
