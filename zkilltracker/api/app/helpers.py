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
