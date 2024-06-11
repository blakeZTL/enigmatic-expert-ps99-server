from dataclasses import asdict, dataclass
from typing import List, Dict
from datetime import datetime
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
        key: str = clan.Name + "||" + str(datetime.now().isoformat())
        doc_ref: DocumentReference = collection.document(key)
        doc_ref.set(asdict(clan))

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
            print(f"No point contributions found for {battle_api_record["BattleID"] if "BattleID" in battle_api_record else "Unknown"}")
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


def write_clan(clan: apiClan, db: Client) -> bool:
    if clan is None:
        return False
    collection: CollectionReference = db.collection("clans")
    key: str = clan.Name + "||" + str(datetime.now().isoformat())
    doc_ref: DocumentReference = collection.document(key)
    doc_ref.set(asdict(clan))
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


def write_roblox_users(users: List[RobloxUser], db: Client) -> bool:
    if len(users) == 0:
        return False
    collection: CollectionReference = db.collection("roblox_users")

    for user in users:
        key: str = str(user.id)
        doc_ref: DocumentReference = collection.document(key)
        doc_ref.set(asdict(user))

    return True


if __name__ == "__main__":
    exit()
