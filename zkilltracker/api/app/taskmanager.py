import requests
from app import app, db
from app.models import Corporation, Kills, MemberKills, Members
import datetime
import time


class KillRefreshTask:
    def __init__(self, run_id):
        self.status = None
        self.run_id = run_id
        self.failed_combinations = list()

    def get_kills(self):
        with app.app_context():
            self.status = "Active"
            corporation_ids = db.session.query(Corporation.id).all()

            current_date = datetime.date.today()
            current_year = current_date.year
            current_month = current_date.month

            if current_month == 1:
                previous_month = 12
            else:
                previous_month = current_month - 1

            failed_combinations = list()

            for corp_id in corporation_ids:
                res_curr = self.get_corp_kills(corp_id[0], current_year, current_month)
                time.sleep(5)
                res_prev = self.get_corp_kills(
                    corp_id[0], current_year - 1, previous_month
                )
                failed_combinations.extend(res_curr)
                failed_combinations.extend(res_prev)
                time.sleep(5)

            self.failed_combinations = failed_combinations
            self.status = "Done"

    def get_corp_kills(self, corporation_id: int, year: int, month: int):
        try:
            existing_kill_ids = db.session.query(Kills.killID).all()
            existing_kill_ids = [kill_id for (kill_id,) in existing_kill_ids]

            iterator = 1
            completed = False

            while not completed:
                url = f"https://zkillboard.com/api/kills/corporationID/{corporation_id}/year/{year}/month/{month}/page/{iterator}/"
                response = requests.get(url)
                data = response.json()

                kill_data = []
                attacker_data = []

                for kill in data:
                    kill_id = kill.get("killmail_id", 0)
                    if kill_id not in existing_kill_ids:
                        kill_hash = kill.get("zkb").get("hash")

                        esi_url = f"https://esi.evetech.net/latest/killmails/{kill_id}/{kill_hash}/"
                        esi_response = requests.get(esi_url)
                        esi_data = esi_response.json()

                        kill_data.append(
                            Kills(
                                killID=kill_id,
                                killHash=kill_hash,
                                locationID=kill.get("zkb").get("locationID"),
                                totalValue=kill.get("zkb").get("totalValue"),
                                points=kill.get("zkb").get("points"),
                                npc=kill.get("zkb").get("npc"),
                                solo=kill.get("zkb").get("solo"),
                                awox=kill.get("zkb").get("awox"),
                                datetime=esi_data.get("killmail_time"),
                                shipTypeID=esi_data.get("victim").get("ship_type_id"),
                            )
                        )

                        attackers = esi_data.get("attackers")
                        for attacker in attackers:
                            if attacker.get("alliance_id") == 99011223:
                                attacker_data.append(
                                    MemberKills(
                                        killID=kill_id,
                                        characterID=attacker.get("character_id"),
                                        damageDone=attacker.get("damage_done"),
                                        finalBlow=attacker.get("final_blow"),
                                        shipTypeID=attacker.get("ship_type_id"),
                                    )
                                )

                if len(data) < 200:
                    completed = True
                else:
                    iterator += 1

                # Insert or update the kill and member kill data
                db.session.bulk_save_objects(kill_data)
                db.session.bulk_save_objects(attacker_data)
                db.session.commit()
            return []

        except Exception as _:
            db.session.rollback()
            return [[corporation_id, month, year]]


class MemberRefreshTask:
    def __init__(self, run_id):
        self.status = None
        self.run_id = run_id

    def fill_members(self):
        with app.app_context():
            self.status = "Active"

            corporation_ids = db.session.query(Corporation.id).all()
            for corp_id in corporation_ids:
                self.fill_members_corp(corporation_id=corp_id[0])

            self.status = "Done"

    def fill_members_corp(self, corporation_id: int):
        try:
            response = requests.get(f"https://evewho.com/api/corplist/{corporation_id}")
            data = response.json()

            all_api_chars = []
            for char in data["characters"]:
                all_api_chars.append(
                    [char["character_id"], char["name"], corporation_id]
                )

            members_to_add = []
            members_to_update = []

            db_members = Members.query.all()
            db_members_dict = {member.characterID: member for member in db_members}

            api_char_ids = {char[0] for char in all_api_chars}

            for char_id, name, corp_id in all_api_chars:
                if char_id not in db_members_dict:
                    members_to_add.append(
                        Members(
                            characterID=char_id,
                            characterName=name,
                            corporationID=corp_id,
                        )
                    )
                else:
                    member = db_members_dict[char_id]
                    if member.corporationID != corp_id:
                        member.corporationID = corp_id
                        members_to_update.append(member)

            for member in db_members:
                if (
                    member.corporationID == corporation_id
                    and member.characterID not in api_char_ids
                ):
                    member.corporationID = None
                    members_to_update.append(member)

            if members_to_add:
                db.session.bulk_save_objects(members_to_add)

            if members_to_update:
                db.session.bulk_save_objects(members_to_update)

            db.session.commit()

        except Exception as e:
            print(e)
            db.session.rollback()
