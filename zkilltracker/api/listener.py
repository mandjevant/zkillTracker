import asyncio
import aiohttp
import sqlite3
import json
from datetime import datetime

DB_PATH = "instance/zkillboard_stats.db"


async def execute_query(query, params):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        conn.rollback()
    finally:
        conn.close()


async def save_kill_to_db(data):
    try:
        kill_id = data.get("killID", 0)
        print(f"Saving kill to db {kill_id}")
        cursor = sqlite3.connect(DB_PATH).cursor()
        cursor.execute("SELECT 1 FROM Kills WHERE killID = ?", (kill_id,))
        if cursor.fetchone():
            return

        kill_hash = data.get("zkb", {}).get("hash")
        esi_url = f"https://esi.evetech.net/latest/killmails/{kill_id}/{kill_hash}/"
        async with aiohttp.ClientSession() as session:
            async with session.get(esi_url) as response:
                esi_data = await response.json()
        print(esi_data)

        query_kills = """INSERT INTO Kills (killID, killHash, locationID, totalValue, points, npc, solo, awox, datetime, shipTypeID)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        params_kills = (
            kill_id,
            kill_hash,
            data.get("zkb", {}).get("locationID"),
            data.get("zkb", {}).get("totalValue"),
            data.get("zkb", {}).get("points"),
            data.get("zkb", {}).get("npc"),
            data.get("zkb", {}).get("solo"),
            data.get("zkb", {}).get("awox"),
            datetime.fromisoformat(
                esi_data.get("killmail_time").replace("Z", "+00:00")
            ),
            esi_data.get("victim", {}).get("ship_type_id"),
        )
        await execute_query(query_kills, params_kills)

        attackers = esi_data.get("attackers", [])
        for attacker in attackers:
            if attacker.get("alliance_id") == 99011223:
                query_attackers = """INSERT INTO MemberKills (killID, characterID, damageDone, finalBlow, shipTypeID)
                                    VALUES (?, ?, ?, ?, ?)"""
                params_attackers = (
                    kill_id,
                    attacker.get("character_id"),
                    attacker.get("damage_done"),
                    attacker.get("final_blow"),
                    attacker.get("ship_type_id"),
                )
                await execute_query(query_attackers, params_attackers)
    except Exception as e:
        print(f"Error saving kill to database: {e}")


async def save_loss_to_db(data):
    try:
        kill_id = data.get("killID", 0)
        print(f"Saving loss to db {kill_id}")
        cursor = sqlite3.connect(DB_PATH).cursor()
        cursor.execute("SELECT 1 FROM Losses WHERE killID = ?", (kill_id,))
        if cursor.fetchone():
            return

        kill_hash = data.get("zkb", {}).get("hash")
        esi_url = f"https://esi.evetech.net/latest/killmails/{kill_id}/{kill_hash}/"
        async with aiohttp.ClientSession() as session:
            async with session.get(esi_url) as response:
                esi_data = await response.json()
        print(esi_data)

        query_losses = """INSERT INTO Losses (killID, killHash, locationID, totalValue, points, npc, solo, awox, datetime, shipTypeID)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        params_losses = (
            kill_id,
            kill_hash,
            data.get("zkb", {}).get("locationID"),
            data.get("zkb", {}).get("totalValue"),
            data.get("zkb", {}).get("points"),
            data.get("zkb", {}).get("npc"),
            data.get("zkb", {}).get("solo"),
            data.get("zkb", {}).get("awox"),
            datetime.fromisoformat(
                esi_data.get("killmail_time").replace("Z", "+00:00")
            ),
            esi_data.get("victim", {}).get("ship_type_id"),
        )
        await execute_query(query_losses, params_losses)
    except Exception as e:
        print(f"Error saving loss to database: {e}")


async def start_websocket_listener():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect("wss://zkillboard.com/websocket/") as ws:
            await ws.send_str(
                json.dumps({"action": "sub", "channel": "alliance:99011223"})
            )
            while True:
                print("Connected and listening to alliance")
                msg = await ws.receive()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    print(data)
                    if data.get("alliance_id") == 99011223:
                        await save_loss_to_db(data)
                    else:
                        await save_kill_to_db(data)


if __name__ == "__main__":
    print("Starting listener")
    asyncio.run(start_websocket_listener())
