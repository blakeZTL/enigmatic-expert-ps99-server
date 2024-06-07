from dataclasses import dataclass
from datetime import date
import datetime
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
class dbClanTotal:
    [key: str]: apiClanTotal
    

def get_clan_totals(pageSize:int=50, sort:str="Points", sortOrder:str="desc")->list[apiClanTotal]:
    clan_totals=[]
    url =f"https://biggamesapi.io/api/clans?page=1&pageSize={pageSize}&sort={sort}&sortOrder={sortOrder}"
    response = requests.get(url)
    if not response.ok:
        return clan_totals
    if "data" not in response.json():
        return clan_totals
    for clan in response.json()["data"]:
        clan_record=apiClanTotal(
            Name=clan["Name"],
            DepositedDiamonds= clan["DepositedDiamonds"],
            Members= clan["Members"] + 1,
            Points= clan["Points"]
        )
        key:str = clan["Name"]+str(datetime.datetime.now().isoformat())
        clan_totals.append({key:dbClanTotal(clan_record)})

    return clan_totals

def write_clan_totals(clan_totals:list[apiClanTotal], db: Client)->bool:
    if len(clan_totals) == 0:
        return False
    collection: CollectionReference = db.collection("clan_totals")

    for key, value in clan_totals.items():
        doc_ref: DocumentReference = collection.document(key)
        doc_ref.set(value)        

    return True

if __name__ == "__main__":
    db = get_db()
    if db is None:
        print("Failed to get database.")
    else:
        print("Database connected successfully.")
        clan_totals = get_clan_totals()
        write_clan_totals(clan_totals, db)
        print("Clan totals written to database.")