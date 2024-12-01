from app import db

class Corporation(db.Model):
    __tablename__ = "corporation"

    id = db.Column(db.Integer, primary_key=True)
    allianceID = db.Column(db.Integer, nullable=True)
    ceoID = db.Column(db.Integer, nullable=False)
    dateFounded = db.Column(db.String, nullable=False)
    memberCount = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    taxRate = db.Column(db.REAL, nullable=False)
    ticker = db.Column(db.String, nullable=False)
    soloKills = db.Column(db.Integer, nullable=False)
    soloLosses = db.Column(db.Integer, nullable=False)
    avgGangSize = db.Column(db.REAL, nullable=False)
    iskLost = db.Column(db.Integer, nullable=False)
    attackersLost = db.Column(db.Integer, nullable=False)
    shipsDestroyed = db.Column(db.Integer, nullable=False)
    iskDestroyed = db.Column(db.Integer, nullable=False)
    attackersDestroyed = db.Column(db.Integer, nullable=False)

    def __init__(self, id, allianceID, ceoID, dateFounded, memberCount, name, taxRate, ticker, soloKills, soloLosses, avgGangSize, iskLost, attackersLost, shipsDestroyed, iskDestroyed, attackersDestroyed):
        self.id = id
        self.allianceID = allianceID
        self.ceoID = ceoID
        self.dateFounded = dateFounded
        self.memberCount = memberCount
        self.name = name
        self.taxRate = taxRate
        self.ticker = ticker
        self.soloKills = soloKills
        self.soloLosses = soloLosses
        self.avgGangSize = avgGangSize
        self.iskLost = iskLost
        self.attackersLost = attackersLost
        self.shipsDestroyed = shipsDestroyed
        self.iskDestroyed = iskDestroyed
        self.attackersDestroyed = attackersDestroyed


class Months(db.Model):
    __tablename__ = "months"

    corporationID = db.Column(db.Integer, db.ForeignKey(Corporation.id), primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, primary_key=True)
    shipsLost = db.Column(db.Integer, nullable=False)
    pointsLost = db.Column(db.Integer, nullable=False)
    iskLost = db.Column(db.Integer, nullable=False)
    shipsDestroyed = db.Column(db.Integer, nullable=False)
    pointsDestroyed = db.Column(db.Integer, nullable=False)
    iskDestroyed = db.Column(db.Integer, nullable=False)

    def __init__(self, corporationID, year, month, shipsLost, pointsLost, iskLost, shipsDestroyed, pointsDestroyed, iskDestroyed):
        self.corporationID = corporationID
        self.year = year
        self.month = month
        self.shipsLost = shipsLost
        self.pointsLost = pointsLost
        self.iskLost = iskLost
        self.shipsDestroyed = shipsDestroyed
        self.pointsDestroyed = pointsDestroyed
        self.iskDestroyed = iskDestroyed
