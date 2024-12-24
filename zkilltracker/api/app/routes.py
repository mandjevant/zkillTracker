from flask import jsonify, request
from app import app, db
from app.models import (
    Months,
    Corporation,
    Alliance,
    Members,
    Kills,
    MemberKills,
    Items,
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
)
from sqlalchemy import func, extract
from app.populators import add_corp
from app.taskmanager import KillRefreshTask, MemberRefreshTask
import uuid
import threading


active_task = None


@app.route("/corporation/<int:corporation_id>/months", methods=["GET"])
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
def get_corporation(corporation_id: int):
    corporation = db.session.query(Corporation).filter_by(id=corporation_id).first()
    if corporation is None:
        return jsonify({"error": "Corporation not found"}), 404

    return jsonify(serialize_corporation(corporation))


@app.route("/corporations", methods=["GET"])
def get_all_corporations():
    corporations = db.session.query(Corporation).all()

    return jsonify([serialize_corporation(corp) for corp in corporations])


@app.route("/get_alliance_data", methods=["GET"])
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
def get_corporation_members(corporation_id: int):
    members = (
        db.session.query(Members).filter(Members.corporationID == corporation_id).all()
    )

    if not members:
        return jsonify({"error": "Corporation not found or has no members"}), 404

    return jsonify([serialize_member(member) for member in members])


@app.route("/corporation/add/<int:corporation_id>")
def add_corporation(corporation_id: int):
    existing_corporation = (
        db.session.query(Corporation).filter_by(id=corporation_id).first()
    )

    if existing_corporation:
        return jsonify({"error": "Corporation already exists"}), 400

    return jsonify(add_corp(corporation_id))


@app.route("/member/<int:character_id>/monthlyaggregations", methods=["GET"])
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


@app.route("/member/<int:character_id>/aggregations", methods=["GET"])
def get_member_aggregations(character_id: int):
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
        .all()
    )

    return jsonify([serialize_aggregations(agg) for agg in results])


@app.route("/member/<int:character_id>/kills/all", methods=["GET"])
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
def task_status(task_id: str):
    global active_task
    if active_task == None:
        return jsonify({"error": "No refresh tasks were started"}), 400

    if active_task.run_id != task_id:
        return jsonify({"error": f"Refresh task with id {task_id} is unknown"}), 400

    if active_task.run_id == task_id:
        return jsonify({"status": active_task.status})


@app.route("/members/add", methods=["GET"])
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
