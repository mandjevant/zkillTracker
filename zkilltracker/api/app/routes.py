from app.models import Months, Corporation
from app import app, db
from flask import jsonify
from app.helpers import serialize_corporation, serialize_month


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
    