from dataclasses import asdict, dataclass
from typing import List, Dict
from datetime import datetime
from database import get_db
import requests
from google.cloud.firestore import Client, CollectionReference, DocumentReference


@dataclass
class apiClanTotal:
    Name: str
    DepositedDiamonds: int
    Members: int
    Points: int

@dataclass
class apiPointContribution:
    UserID: int
    Points: int

@dataclass
class apiBattle:
    BattleID: int
    Points: int
    PointContributions: List[apiPointContribution]
    EarnedMedal: str

@dataclass
class apiDiamondContribution:
    UserID: int
    Diamonds: int

@dataclass
class apiClan:
    Owner: int
    Name: str
    Icon: str
    Desc: str
    Members: List[Dict]
    DepositedDiamonds: int
    DiamondContributions: List[apiDiamondContribution]
    Status: str
    Battles: List[apiBattle]


def get_clan_totals(
    pageSize: int = 50, sort: str = "Points", sortOrder: str = "desc"
) -> List[apiClanTotal]:
    clan_totals: List[apiClanTotal] = []
    url = f"https://biggamesapi.io/api/clans?page=1&pageSize={pageSize}&sort={sort}&sortOrder={sortOrder}"
    response = requests.get(url)
    if not response.ok:
        return clan_totals
    if "data" not in response.json():
        return clan_totals
    for clan in response.json()["data"]:
        clan_record = apiClanTotal(
            Name=clan["Name"],
            DepositedDiamonds=clan["DepositedDiamonds"],
            Members=clan["Members"] + 1,
            Points=clan["Points"],
        )
        clan_totals.append(clan_record)

    return clan_totals


def write_clan_totals(clan_totals: List[apiClanTotal], db: Client) -> bool:
    if len(clan_totals) == 0:
        return False
    collection: CollectionReference = db.collection("clan_totals")

    for clan in clan_totals:
        key: str = clan.Name +"||"+ str(datetime.now().isoformat())
        doc_ref: DocumentReference = collection.document(key)
        doc_ref.set(asdict(clan))

    return True


def get_clan(
    clan_name: str,
) -> apiClanTotal:
    url = f"https://biggamesapi.io/api/clan/{clan_name}"
    response = requests.get(url)
    if not response.ok:
        return None
    if "data" not in response.json():
        return None
    clan = response.json()["data"]
    deposited_diamonds: List[apiDiamondContribution] = []
    for member in clan["DiamondContributions"]["AllTime"]["Data"]:
        diamond_record = apiDiamondContribution(
            UserID= member["UserID"], # This is not in the response
            Diamonds= member["Diamonds"]
        )
        deposited_diamonds.append(diamond_record)
    battles: List[apiBattle] = []
    for _battle, value in clan["Battles"].items(): 
        point_contributions = []
        for point in value["PointContributions"]:
            point_record = apiPointContribution(
                UserID= point["UserID"], # This is not in the response
                Points= point["Points"]
            )
            point_contributions.append(point_record)
        battle_record = apiBattle(
            BattleID=value["BattleID"],
            Points=value["Points"],
            PointContributions=point_contributions,
            EarnedMedal=value["EarnedMedal"] if "EarnedMedal" in value else "Unknown"
        )
        battles.append(battle_record)        
    
    clan_record = apiClan(
        Owner=clan["Owner"],
        Name=clan["Name"],
        Icon=clan["Icon"],
        Desc=clan["Desc"],
        Members=clan["Members"],
        DepositedDiamonds=clan["DepositedDiamonds"],
        DiamondContributions=deposited_diamonds,
        Status=clan["Status"] if "Status" in clan else "",
        Battles=clan["Battles"],    
    )
    return clan_record

def write_clan(clan: apiClan, db: Client) -> bool:
    if clan is None:
        return False
    collection: CollectionReference = db.collection("clans")
    key: str = clan.Name +"||"+ str(datetime.now().isoformat())
    doc_ref: DocumentReference = collection.document(key)
    doc_ref.set(asdict(clan))
    return True

if __name__ == "__main__":
    db = get_db()
    if db is None:
        print("Failed to get database.")
    else:
        print("Database connected successfully.")
        clan_totals = get_clan_totals()
        if write_clan_totals(clan_totals, db):
            print("Clan totals written to database.")
        else:
            print("Failed to write clan totals to database.")
        for clan in clan_totals:
            clan = get_clan(clan.Name)
            if write_clan(clan, db):
                print("Clan written to database.")
            else:
                print("Failed to write clan to database.")