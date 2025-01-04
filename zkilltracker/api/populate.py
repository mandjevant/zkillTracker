import sqlite3
import requests
import json

# # Fetch the JSON data from the API
# MCAPcorporationID = 98753041
# corporation_id = 98701358

# corps = [98657866, 98699454, 98689072, 98637264, 98659687, 98680640, 1673385956, 98567310, 98525766, 98128247, 98721819, 98769211, 98592686, 98729885, 742354696, 98486364, 98745839, 98683163, 98732136, 98558667, 98764503, 98699180, 98733072, 98767682, 146531499, 98624572, 98651543, 742911959 ]
# months_entries_entries = list()
# corporation_entries = list()
# for corporation_id in corps:
#     url = f"https://zkillboard.com/api/stats/corporationID/{corporation_id}/"
#     response = requests.get(url)
#     data = response.json()

#     # Extract the required data for the 'months' table
#     months_data = data.get('months', {})


#     months_entries = []
#     for month, stats in months_data.items():
#         year = month[:4]
#         month = month[4:]
#         entry = (
#             corporation_id,
#             int(year),
#             int(month),
#             stats.get('shipsLost', 0),
#             stats.get('pointsLost', 0),
#             stats.get('iskLost', 0),
#             stats.get('shipsDestroyed', 0),
#             stats.get('pointsDestroyed', 0),
#             stats.get('iskDestroyed', 0)
#         )
#         months_entries.append(entry)

#     # Extract the required data for the 'corporation' table
#     print(corporation_id)
#     info = data.get('info', {})
#     corporation_entry = (
#         corporation_id,
#         info.get('allianceID', 0),
#         info.get('ceoID', 0),
#         info.get('date_founded', ''),
#         info.get('memberCount', 0),
#         info.get('name', ''),
#         info.get('taxRate', 0),
#         info.get('ticker', ''),
#         data.get('soloKills', 0),
#         data.get('soloLosses', 0),
#         data.get('avgGangSize', 0),
#         data.get('iskLost', 0),
#         data.get('attackersLost', 0),
#         data.get('shipsDestroyed', 0),
#         data.get('iskDestroyed', 0),
#         data.get('attackersDestroyed', 0)
#     )
#     months_entries_entries.extend(months_entries)
#     corporation_entries.append(corporation_entry)

# # print(months_entries_entries)
# # print(corporation_entries)


# # Create the SQLite3 database and tables
# conn = sqlite3.connect('instance/zkillboard_stats.db')
# cursor = conn.cursor()

# # cursor.execute('''
# # CREATE TABLE IF NOT EXISTS months (
# #     corporationID INTEGER,
# #     year INTEGER,
# #     month INTEGER,
# #     shipsLost INTEGER,
# #     pointsLost INTEGER,
# #     iskLost INTEGER,
# #     shipsDestroyed INTEGER,
# #     pointsDestroyed INTEGER,
# #     iskDestroyed INTEGER,
# #     PRIMARY KEY (corporationID, year, month)
# # )
# # ''')

# # cursor.execute('''
# # CREATE TABLE IF NOT EXISTS corporation (
# #     id INTEGER PRIMARY KEY,
# #     allianceID INTEGER,
# #     ceoID INTEGER,
# #     dateFounded TEXT,
# #     memberCount INTEGER,
# #     name TEXT,
# #     taxRate REAL,
# #     ticker TEXT,
# #     soloKills INTEGER,
# #     soloLosses INTEGER,
# #     avgGangSize REAL,
# #     iskLost INTEGER,
# #     attackersLost INTEGER,
# #     shipsDestroyed INTEGER,
# #     iskDestroyed INTEGER,
# #     attackersDestroyed INTEGER
# # )
# # ''')

# # import pandas as pd
# # df = pd.read_excel("alliancedatadump.xlsx", header=0)


# # cursor.execute('''
# # CREATE TABLE IF NOT EXISTS alliance (
# #     CorporationTicker VARCHAR(10),
# #     Kills FLOAT,
# #     Mains INT,
# #     ActiveMains INT,
# #     KillsPerActiveMain FLOAT,
# #     PercentageOfAllianceKills VARCHAR(10),
# #     Year INT,
# #     Month INT
# # )
# # ''')

# # df.to_sql('alliance', conn, if_exists='append', index=False)

# # cursor.executemany('''
# # INSERT OR REPLACE INTO alliance (
# #     CorporationTicker, Kills, Mains, ActiveMains, KillsPerActiveMain,
# #     PercentageOfAllianceKills, Year, Month
# # ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
# # ''', alliance_entries)


# # Insert the data into the tables
# cursor.executemany('''
# INSERT OR REPLACE INTO months (
#     corporationID, year, month, shipsLost, pointsLost, iskLost,
#     shipsDestroyed, pointsDestroyed, iskDestroyed
# ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
# ''', months_entries_entries)

# cursor.executemany('''
# INSERT OR REPLACE INTO corporation (
#     id, allianceID, ceoID, dateFounded, memberCount, name, taxRate, ticker,
#     soloKills, soloLosses, avgGangSize, iskLost, attackersLost, shipsDestroyed, iskDestroyed, attackersDestroyed
# ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
# ''', corporation_entries)

# # Commit the changes and close the connection
# conn.commit()
# conn.close()


import yaml
import sqlite3

# Load the YAML file
with open("types.yaml", "r", encoding="utf-8") as file:
    data = yaml.safe_load(file)

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("instance/zkillboard_stats.db")
cursor = conn.cursor()

# Create table
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS items (
    type_id INTEGER PRIMARY KEY,
    name TEXT
)
"""
)

# Insert data into the table
for type_id, item in data.items():
    try:
        name = item["name"]["en"]
        cursor.execute(
            "INSERT INTO items (type_id, name) VALUES (?, ?)", (int(type_id), name)
        )
    except KeyError:
        # If there's an error retrieving the English name, skip this entry
        print(f"Skipping type_id {type_id} due to missing 'name' or 'en' key")

# Commit the transaction and close the connection
conn.commit()
conn.close()

print("Data has been successfully inserted into the SQLite database.")
