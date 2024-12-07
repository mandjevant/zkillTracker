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
        "attackersDestroyed": corp.attackersDestroyed
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
        "iskDestroyed": month.iskDestroyed
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
        "month": entry.month
    }