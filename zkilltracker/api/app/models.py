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

    def __init__(
        self,
        id,
        allianceID,
        ceoID,
        dateFounded,
        memberCount,
        name,
        taxRate,
        ticker,
        soloKills,
        soloLosses,
        avgGangSize,
        iskLost,
        attackersLost,
        shipsDestroyed,
        iskDestroyed,
        attackersDestroyed,
    ):
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

    def __repr__(self):
        return f"<Corporation id={self.id}, allianceID={self.allianceID}, ceoID={self.ceoID}, dateFounded={self.dateFounded}, memberCount={self.memberCount}, name={self.name}, taxRate={self.taxRate}, ticker={self.ticker}, soloKills={self.soloKills}, soloLosses={self.soloLosses}, avgGangSize={self.avgGangSize}, iskLost={self.iskLost}, attackersLost={self.attackersLost}, shipsDestroyed={self.shipsDestroyed}, iskDestroyed={self.iskDestroyed}, attackersDestroyed={self.attackersDestroyed}>"


class Months(db.Model):
    __tablename__ = "months"

    corporationID = db.Column(
        db.Integer, db.ForeignKey(Corporation.id), primary_key=True
    )
    year = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, primary_key=True)
    shipsLost = db.Column(db.Integer, nullable=False)
    pointsLost = db.Column(db.Integer, nullable=False)
    iskLost = db.Column(db.Integer, nullable=False)
    shipsDestroyed = db.Column(db.Integer, nullable=False)
    pointsDestroyed = db.Column(db.Integer, nullable=False)
    iskDestroyed = db.Column(db.Integer, nullable=False)

    def __init__(
        self,
        corporationID,
        year,
        month,
        shipsLost,
        pointsLost,
        iskLost,
        shipsDestroyed,
        pointsDestroyed,
        iskDestroyed,
    ):
        self.corporationID = corporationID
        self.year = year
        self.month = month
        self.shipsLost = shipsLost
        self.pointsLost = pointsLost
        self.iskLost = iskLost
        self.shipsDestroyed = shipsDestroyed
        self.pointsDestroyed = pointsDestroyed
        self.iskDestroyed = iskDestroyed

    def __repr__(self):
        return f"<Months corporationID={self.corporationID}, year={self.year}, month={self.month}, shipsLost={self.shipsLost}, pointsLost={self.pointsLost}, iskLost={self.iskLost}, shipsDestroyed={self.shipsDestroyed}, pointsDestroyed={self.pointsDestroyed}, iskDestroyed={self.iskDestroyed}>"


class Alliance(db.Model):
    __tablename__ = "alliance"

    corporationTicker = db.Column(
        db.String, db.ForeignKey("corporation.ticker"), primary_key=True
    )
    kills = db.Column(db.Integer, nullable=False)
    mains = db.Column(db.Integer, nullable=False)
    activeMains = db.Column(db.Integer, nullable=False)
    killsPerActiveMain = db.Column(db.Float, nullable=False)
    percentageOfAllianceKills = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, primary_key=True)

    def __init__(
        self,
        corporationTicker,
        kills,
        mains,
        activeMains,
        killsPerActiveMain,
        percentageOfAllianceKills,
        year,
        month,
    ):
        self.corporationTicker = corporationTicker
        self.kills = kills
        self.mains = mains
        self.activeMains = activeMains
        self.killsPerActiveMain = killsPerActiveMain
        self.percentageOfAllianceKills = percentageOfAllianceKills
        self.year = year
        self.month = month

    def __repr__(self):
        return f"<Alliance corporationTicker={self.corporationTicker}, kills={self.kills}, mains={self.mains}, activeMains={self.activeMains}, killsPerActiveMain={self.killsPerActiveMain}, percentageOfAllianceKills={self.percentageOfAllianceKills}, year={self.year}, month={self.month}>"


class Members(db.Model):
    __tablename__ = "members"

    characterID = db.Column(db.Integer, primary_key=True)
    characterName = db.Column(db.String, nullable=False)
    corporationID = db.Column(
        db.Integer, db.ForeignKey("corporation.id"), nullable=False
    )

    def __init__(self, characterID, characterName, corporationID):
        self.characterID = characterID
        self.characterName = characterName
        self.corporationID = corporationID

    def __repr__(self):
        return f"<Members characterID={self.characterID}, characterName={self.characterName}, corporationID={self.corporationID}>"


class Kills(db.Model):
    __tablename__ = "kills"

    killID = db.Column(db.Integer, primary_key=True)
    killHash = db.Column(db.String, nullable=False)
    locationID = db.Column(db.Integer, nullable=False)
    totalValue = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    npc = db.Column(db.Integer, nullable=False)
    solo = db.Column(db.Integer, nullable=False)
    awox = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.String, nullable=False)
    shipTypeID = db.Column(db.Integer, nullable=False)

    def __init__(
        self,
        killID,
        killHash,
        locationID,
        totalValue,
        points,
        npc,
        solo,
        awox,
        datetime,
        shipTypeID,
    ):
        self.killID = killID
        self.killHash = killHash
        self.locationID = locationID
        self.totalValue = totalValue
        self.points = points
        self.npc = npc
        self.solo = solo
        self.awox = awox
        self.datetime = datetime
        self.shipTypeID = shipTypeID

    def __repr__(self):
        return f"<Kills killID={self.killID}, killHash={self.killHash}, locationID={self.locationID}, totalValue={self.totalValue}, points={self.points}, npc={self.npc}, solo={self.solo}, awox={self.awox}, datetime={self.datetime}, shipTypeID={self.shipTypeID}>"


class MemberKills(db.Model):
    __tablename__ = "memberKills"

    killID = db.Column(db.Integer, db.ForeignKey("kills.killID"), primary_key=True)
    characterID = db.Column(
        db.Integer, db.ForeignKey("members.characterID"), primary_key=True
    )
    damageDone = db.Column(db.Integer, nullable=False)
    finalBlow = db.Column(db.Integer, nullable=False)
    shipTypeID = db.Column(db.Integer, nullable=True)

    def __init__(self, killID, characterID, damageDone, finalBlow, shipTypeID):
        self.killID = killID
        self.characterID = characterID
        self.damageDone = damageDone
        self.finalBlow = finalBlow
        self.shipTypeID = shipTypeID

    def __repr__(self):
        return f"<MemberKills killID={self.killID}, damageDone={self.damageDone}, finalBlow={self.finalBlow}, shipTypeID={self.shipTypeID}>"


class Items(db.Model):
    __tablename__ = "items"

    type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __init__(self, type_id, name):
        self.type_id = type_id
        self.name = name

    def __repr__(self):
        return f"<Items type_id={self.type_id}, name={self.name}>"


class ApprovedCharacters(db.Model):
    __tablename__ = "approvedCharacters"

    characterID = db.Column(db.Integer, primary_key=True)

    def __init__(self, characterID):
        self.characterID = characterID

    def __repr__(self):
        return f"<ApprovedCharacters characterID={self.characterID}>"


class AdminCharacters(db.Model):
    __tablename__ = "adminCharacters"

    characterID = db.Column(db.Integer, primary_key=True)

    def __init__(self, characterID):
        self.characterID = characterID

    def __repr__(self):
        return f"<AdminCharacters characterID={self.characterID}>"
