from flask import jsonify, request, redirect, session
from app import (
    app,
    db,
    EVE_AUTH_URL,
    EVE_REDIRECT_URI,
    EVE_CLIENT_ID,
)
from app.models import (
    Months,
    Corporation,
    Alliance,
    Members,
    Kills,
    MemberKills,
    Items,
    AdminCharacters,
    ApprovedCharacters,
)
from app.helpers import (
    serialize_corporation,
    serialize_month,
    serialize_alliance,
    serialize_aggregations,
    serialize_member,
    serialize_kills,
    serialize_member_kills,
    serialize_items,
    serialize_month_progress,
    get_payload,
)
from sqlalchemy import func, extract
from app.populators import add_corp
from app.taskmanager import KillRefreshTask, MemberRefreshTask
from app.decorators import login_required, admin_required
import threading
import uuid


active_task = None


@app.route("/login")
def login():
    auth_url = f"{EVE_AUTH_URL}?response_type=code&state={uuid.uuid4()}&redirect_uri={EVE_REDIRECT_URI}&client_id={EVE_CLIENT_ID}"
    return auth_url


@app.route("/oauth-callback/", methods=["GET"])
def oauth_callback():
    auth_code = request.args.get("code")
    if auth_code:
        get_payload(auth_code)
    return redirect("http://localhost:3000/"), 200


@app.route("/check_approval")
def check_approval():
    character_id = session.get("character_id")
    character_name = session.get("character_name")
    if not character_id:
        return jsonify({"status": "in_progress"})

    approved_character = ApprovedCharacters.query.filter_by(
        characterID=character_id
    ).first()
    print(approved_character)
    if approved_character:
        session["logged_in"] = True
        admin_character = AdminCharacters.query.filter_by(
            characterID=character_id
        ).first()
        session["is_admin"] = bool(admin_character)
        return jsonify(
            {
                "status": "Done",
                "logged_in": True,
                "is_admin": bool(admin_character),
                "character_name": character_name,
            }
        )
    else:
        return (
            jsonify(
                {
                    "status": "False",
                    "logged_in": False,
                    "is_admin": False,
                    "character_name": None,
                }
            ),
            400,
        )


@app.route("/check_logged_in")
def check_logged_in():
    logged_in = session.get("logged_in", False)
    is_admin = session.get("is_admin", False)
    character_name = session.get("character_name", False)
    return jsonify(
        {
            "logged_in": logged_in,
            "is_admin": is_admin,
            "character_name": character_name,
        }
    )


@app.route("/logout")
@login_required
def logout():
    session["logged_in"] = False
    session["is_admin"] = False
    session["character_name"] = None
    return jsonify(
        {
            "logged_in": session["logged_in"],
            "is_admin": session["is_admin"],
            "character_name": session["character_name"],
        }
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
    corporations = db.session.query(Corporation).all()

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

    return jsonify([serialize_alliance(entry) for entry in result])


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


@app.route("/corporation/add/<int:corporation_id>")
@login_required
def add_corporation(corporation_id: int):
    existing_corporation = (
        db.session.query(Corporation).filter_by(id=corporation_id).first()
    )

    if existing_corporation:
        return jsonify({"error": "Corporation already exists"}), 400

    return jsonify(add_corp(corporation_id))


@app.route("/member/<int:character_id>/monthlyaggregations", methods=["GET"])
@login_required
def get_member_monthly_aggregations(character_id: int):
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

    return jsonify([serialize_aggregations(agg) for agg in results])


import datetime
from dateutil.relativedelta import relativedelta


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


# @app.route("/member/<int:character_id>/aggregations", methods=["GET"])
# @login_required
# def get_member_aggregations(character_id: int):
#     results = (
#         db.session.query(
#             func.strftime("%Y-%m", Kills.datetime).label("year_month"),
#             func.sum(Kills.totalValue).label("totalValue"),
#             func.sum(Kills.points).label("points"),
#             func.sum(Kills.npc).label("npc"),
#             func.sum(Kills.solo).label("solo"),
#             func.sum(Kills.awox).label("awox"),
#             func.count().label("killCount"),
#         )
#         .select_from(MemberKills)
#         .join(Kills, MemberKills.killID == Kills.killID)
#         .filter(MemberKills.characterID == character_id)
#         .all()
#     )

#     return jsonify([serialize_aggregations(agg) for agg in results])


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
    "/member/<int:character_id>/change_corporation/<int:corporation_id>",
    methods=["PUT"],
)
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
    "/members/add/<int:character_id>/<string:character_name>/<int:corporation_id>",
    methods=["POST"],
)
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
@admin_required
def add_kills():
    global active_task
    if active_task is not None:
        if active_task.status == "Done":
            active_task = None

    if active_task is None:
        uniq_id = uuid.uuid4()
        newTask = KillRefreshTask(run_id=uniq_id)
        active_task = newTask
        threading.Thread(target=newTask.get_kills).start()

        return jsonify({"task_id": uniq_id})
    else:
        return jsonify({"error": "A refresh task is currently active"}), 400


@app.route("/task/status/<string:task_id>", methods=["GET"])
@admin_required
def task_status(task_id: str):
    global active_task
    if active_task == None:
        return jsonify({"error": "No refresh tasks were started"}), 400

    if active_task.run_id != task_id:
        return jsonify({"error": f"Refresh task with id {task_id} is unknown"}), 400

    if active_task.run_id == task_id:
        return jsonify({"status": active_task.status})


@app.route("/members/add", methods=["GET"])
@admin_required
def add_members():
    global active_task
    if active_task is not None:
        if active_task.status == "Done":
            active_task = None

    if active_task is None:
        uniq_id = uuid.uuid4()
        newTask = MemberRefreshTask(run_id=uniq_id)
        active_task = newTask
        threading.Thread(target=newTask.fill_members).start()

        return jsonify({"task_id": uniq_id})
    else:
        return jsonify({"error": "A refresh task is currently active"}), 400


@app.route("/items", methods=["GET"])
def get_items():
    all_items = db.session.query(Items).all()
    return jsonify([serialize_items(item) for item in all_items])
