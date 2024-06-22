from dataclasses import asdict, dataclass
from typing import List, Dict
from datetime import datetime
import pymongo.collection
import requests
import pymongo.database
from pymongo.results import InsertManyResult


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
class apiClanMember:
    UserID: int
    PermissionLevel: int
    JoinTime: int


@dataclass
class apiClan:
    Owner: int
    Name: str
    Icon: str
    Desc: str
    Members: List[apiClanMember]
    DepositedDiamonds: int
    DiamondContributions: List[apiDiamondContribution]
    Status: str
    Battles: List[apiBattle]


def get_clan_totals(
    pageSize: int = 50, sort: str = "Points", sortOrder: str = "desc"
) -> List[apiClanTotal]:
    page = 1
    clan_totals: List[apiClanTotal] = []
    url = f"https://biggamesapi.io/api/clans?page={page}&pageSize={pageSize}&sort={sort}&sortOrder={sortOrder}"
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
    if "SOUP" in [clan.Name for clan in clan_totals]:
        return clan_totals
    page += 1
    while True:
        print(f"Fetching page {page} of clans...")
        url = f"https://biggamesapi.io/api/clans?page={page}&pageSize={pageSize}&sort={sort}&sortOrder={sortOrder}"
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
        if "SOUP" in [clan.Name for clan in clan_totals]:
            return clan_totals
        page += 1


def write_clan_totals(
    clan_totals: List[apiClanTotal], db: pymongo.database.Database
) -> bool:
    if len(clan_totals) == 0:
        return False
    collection: pymongo.collection.Collection = db["clan-totals"]
    new_clan_totals = []
    for clan in clan_totals:
        key: str = clan.Name + "||" + str(datetime.now().isoformat())
        new_clan_total = {
            "Name": clan.Name,
            "DepositedDiamonds": clan.DepositedDiamonds,
            "Members": clan.Members,
            "Points": clan.Points,
            "_id": key,
        }
        new_clan_totals.append(new_clan_total)

    results: InsertManyResult = None
    try:
        results = collection.insert_many(new_clan_totals, ordered=False)
    except pymongo.errors.BulkWriteError as _:
        print("Duplicate key error(s) occurred.")
    finally:
        for new_clan_total in new_clan_totals:
            if (
                (
                    results is not None
                    and results.inserted_ids
                    and new_clan_total["_id"] not in results.inserted_ids
                )
                or not results
                or results.inserted_ids
            ):
                print(f"Failed to insert {new_clan_total['_id']}")
                collection.update_one(
                    {"_id": new_clan_total["_id"]},
                    {"$set": new_clan_total},
                    upsert=True,
                )
                print(f"Updated {new_clan_total['_id']}")

    return True


def get_clan(
    clan_name: str,
) -> apiClan:
    url = f"https://biggamesapi.io/api/clan/{clan_name}"
    response = requests.get(url)
    if not response.ok:
        return None
    if "data" not in response.json():
        return None
    api_data: Dict = response.json()["data"]
    deposited_diamonds: List[apiDiamondContribution] = []
    for member in api_data["DiamondContributions"]["AllTime"]["Data"]:
        diamond_record = apiDiamondContribution(
            UserID=member["UserID"],
            Diamonds=member["Diamonds"],
        )
        deposited_diamonds.append(diamond_record)
    battles: List[apiBattle] = []
    for battle in api_data["Battles"]:
        battle_api_record = api_data["Battles"][battle]
        point_contributions = []
        if "PointContributions" not in battle_api_record:
            print(
                f"No point contributions found for {battle_api_record['BattleID'] if 'BattleID' in battle_api_record else 'Unknown'}"
            )
        else:
            for point in battle_api_record["PointContributions"]:
                point_record = apiPointContribution(
                    UserID=point["UserID"],
                    Points=point["Points"],
                )
                point_contributions.append(point_record)
        battle_record = apiBattle(
            BattleID=(
                battle_api_record["BattleID"]
                if "BattleID" in battle_api_record
                else "Unknown"
            ),
            Points=battle_api_record["Points"] if "Points" in battle_api_record else 0,
            PointContributions=point_contributions,
            EarnedMedal=(
                battle_api_record["EarnedMedal"]
                if "EarnedMedal" in battle_api_record
                else "Unknown"
            ),
        )
        battles.append(battle_record)

    clan_members: List[apiClanMember] = []
    for member in api_data["Members"]:
        clan_members.append(
            apiClanMember(
                UserID=member["UserID"],
                PermissionLevel=member["PermissionLevel"],
                JoinTime=member["JoinTime"],
            )
        )
    clan_members.append(
        apiClanMember(
            UserID=api_data["Owner"],
            PermissionLevel=0,
            JoinTime=0,
        )
    )

    clan_record = apiClan(
        Owner=api_data["Owner"],
        Name=api_data["Name"],
        Icon=api_data["Icon"],
        Desc=api_data["Desc"],
        Members=clan_members,
        DepositedDiamonds=api_data["DepositedDiamonds"],
        DiamondContributions=deposited_diamonds,
        Status=api_data["Status"] if "Status" in api_data else "",
        Battles=battles,
    )
    return clan_record


def write_clan(clan: apiClan, db: pymongo.database.Database) -> bool:
    if clan is None:
        return False
    collection: pymongo.collection.Collection = db["clans"]
    key: str = clan.Name + "||" + str(datetime.now().isoformat())
    new_clans_record = {
        "Owner": clan.Owner,
        "Name": clan.Name,
        "Icon": clan.Icon,
        "Desc": clan.Desc,
        "Members": [asdict(member) for member in clan.Members],
        "DepositedDiamonds": clan.DepositedDiamonds,
        "DiamondContributions": [
            asdict(diamond) for diamond in clan.DiamondContributions
        ],
        "Status": clan.Status,
        "Battles": [asdict(battle) for battle in clan.Battles],
        "_id": key,
    }
    try:
        collection.insert_one(new_clans_record)
    except pymongo.errors.DuplicateKeyError as _:
        print(f"Failed to insert {key}")
        collection.update_one({"_id": key}, {"$set": new_clans_record})

    return True


@dataclass
class RobloxUser:
    hasVerifiedBadge: bool
    id: int
    name: str
    displayName: str


@dataclass
class apiRobloxUserData:
    data: List[RobloxUser]


def get_roblox_users_from_api(user_ids: List[int]) -> List[RobloxUser]:
    url = "https://users.roblox.com/v1/users"
    json_data = {"userIds": user_ids, "excludeBannedUsers": True}
    response = requests.post(url, json=json_data)
    if not response.ok:
        print(response.text)
        return []
    if "data" not in response.json():
        return []
    users = []
    for user in response.json()["data"]:
        user_record = RobloxUser(
            hasVerifiedBadge=user["hasVerifiedBadge"],
            id=user["id"],
            name=user["name"],
            displayName=user["displayName"],
        )
        users.append(user_record)

    return users


def write_roblox_users(users: List[RobloxUser], db: pymongo.database.Database) -> bool:
    if len(users) == 0:
        return False
    collection: pymongo.collection.Collection = db["users"]
    users_records = []
    for user in users:
        # key: str = str(user.id)
        # doc_ref: DocumentReference = collection.document(key)
        # doc_ref.set(asdict(user))
        new_user = {
            "hasVerifiedBadge": user.hasVerifiedBadge,
            "id": user.id,
            "name": user.name,
            "displayName": user.displayName,
            "_id": user.id,
        }
        users_records.append(new_user)
    results: InsertManyResult = None
    try:
        results = collection.insert_many(users_records, ordered=False)
    except pymongo.errors.BulkWriteError as _:
        print("Duplicate key error(s) occurred.")
    finally:
        for user in users_records:
            if (
                (
                    results is not None
                    and results.inserted_ids
                    and user["_id"] not in results.inserted_ids
                )
                or not results
                or results.inserted_ids
            ):
                print(f"Failed to insert {user['_id']}")
                collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": user},
                    upsert=True,
                )
                print(f"Updated {user['_id']}")

    return True


if __name__ == "__main__":
    exit()
