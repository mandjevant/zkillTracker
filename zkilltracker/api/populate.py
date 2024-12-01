import sqlite3
import requests
import json

# Fetch the JSON data from the API
MCAPcorporationID = 98753041
url = "https://zkillboard.com/api/stats/corporationID/98701358/"
response = requests.get(url)
data = response.json()

# Extract the required data for the 'months' table
months_data = data.get('months', {})
corporation_id = 98701358

months_entries = []
for month, stats in months_data.items():
    year = month[:4]
    month = month[4:]
    entry = (
        corporation_id,
        int(year),
        int(month),
        stats.get('shipsLost', 0),
        stats.get('pointsLost', 0),
        stats.get('iskLost', 0),
        stats.get('shipsDestroyed', 0),
        stats.get('pointsDestroyed', 0),
        stats.get('iskDestroyed', 0)
    )
    months_entries.append(entry)

# Extract the required data for the 'corporation' table
info = data.get('info', {})
corporation_entry = (
    corporation_id,
    info.get('allianceID', 0),
    info.get('ceoID', 0),
    info.get('date_founded', ''),
    info.get('memberCount', 0),
    info.get('name', ''),
    info.get('taxRate', 0),
    info.get('ticker', ''),
    data.get('soloKills', 0),
    data.get('soloLosses', 0),
    data.get('avgGangSize', 0),
    data.get('iskLost', 0),
    data.get('attackersLost', 0),
    data.get('shipsDestroyed', 0),
    data.get('iskDestroyed', 0),
    data.get('attackersDestroyed', 0)
)

# Create the SQLite3 database and tables
conn = sqlite3.connect('instance/zkillboard_stats.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS months (
    corporationID INTEGER,
    year INTEGER,
    month INTEGER,
    shipsLost INTEGER,
    pointsLost INTEGER,
    iskLost INTEGER,
    shipsDestroyed INTEGER,
    pointsDestroyed INTEGER,
    iskDestroyed INTEGER,
    PRIMARY KEY (corporationID, year, month)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS corporation (
    id INTEGER PRIMARY KEY,
    allianceID INTEGER,
    ceoID INTEGER,
    dateFounded TEXT,
    memberCount INTEGER,
    name TEXT,
    taxRate REAL,
    ticker TEXT,
    soloKills INTEGER,
    soloLosses INTEGER,
    avgGangSize REAL,
    iskLost INTEGER,
    attackersLost INTEGER,
    shipsDestroyed INTEGER,
    iskDestroyed INTEGER,
    attackersDestroyed INTEGER
)
''')

# Insert the data into the tables
cursor.executemany('''
INSERT OR REPLACE INTO months (
    corporationID, year, month, shipsLost, pointsLost, iskLost,
    shipsDestroyed, pointsDestroyed, iskDestroyed
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', months_entries)

cursor.execute('''
INSERT OR REPLACE INTO corporation (
    id, allianceID, ceoID, dateFounded, memberCount, name, taxRate, ticker,
    soloKills, soloLosses, avgGangSize, iskLost, attackersLost, shipsDestroyed, iskDestroyed, attackersDestroyed
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', corporation_entry)

# Commit the changes and close the connection
conn.commit()
conn.close()
