from app.models import Months, Corporation, Alliance
from app import app, db
from flask import jsonify, request
from app.helpers import serialize_corporation, serialize_month, serialize_alliance


@app.route("/corporation/<int:corporation_id>/months", methods=["GET"])
def get_months_corporation(corporation_id: int):
    months = Months.query.filter_by(corporationID=corporation_id).order_by(Months.year, Months.month).all()
    if len(months) == 0:
        return jsonify({"error": "Corporation not found"}), 404

    return jsonify([serialize_month(month) for month in months])


@app.route("/corporation/<int:corporation_id>", methods=["GET"])
def get_corporation(corporation_id: int):
    corporation = Corporation.query.filter_by(id=corporation_id).first()
    if corporation is None:
        return jsonify({"error": "Corporation not found"}), 404

    return jsonify(serialize_corporation(corporation))


@app.route("/corporations", methods=["GET"])
def get_all_corporations():
    corporations = Corporation.query.all()
    return jsonify([serialize_corporation(corp) for corp in corporations])


@app.route("/get_alliance_data", methods=["GET"])
def get_alliance_data():
    start_year = int(request.args.get("start_year"))
    start_month = int(request.args.get("start_month"))
    end_year = int(request.args.get("end_year"))
    end_month = int(request.args.get("end_month"))
    corporations = request.args.getlist("corporations")

    query = db.session.query(Alliance).filter(
        (Alliance.year > start_year) | 
        ((Alliance.year == start_year) & (Alliance.month >= start_month)),
        (Alliance.year < end_year) | 
        ((Alliance.year == end_year) & (Alliance.month <= end_month))
    )

    result = query.filter(Alliance.corporationTicker.in_(corporations)).all()
    
    return jsonify([serialize_alliance(entry) for entry in result])


@app.route("/get_alliance_tickers", methods=["GET"])
def get_alliance_tickers():
    start_year = int(request.args.get("start_year"))
    start_month = int(request.args.get("start_month"))
    end_year = int(request.args.get("end_year"))
    end_month = int(request.args.get("end_month"))

    results = Alliance.query.filter(
        (Alliance.year > start_year) | ((Alliance.year == start_year) & (Alliance.month >= start_month)),
        (Alliance.year < end_year) | ((Alliance.year == end_year) & (Alliance.month <= end_month))
    ).all()

    return jsonify([serialize_alliance(entry) for entry in results])
    