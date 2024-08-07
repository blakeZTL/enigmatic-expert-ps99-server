from typing import List
import os
from dotenv import load_dotenv
from services import (
    get_clan_totals,
    get_clan,
    write_clan,
    apiClanTotal,
    apiClan,
)

from database import get_db
from pymongo import database
from utils import is_during_active_battle


class DatabaseError(Exception):
    pass


class ClanError(Exception):
    pass


def main():
    if not is_during_active_battle():
        print("Not during active battle.")
        return
    load_dotenv(dotenv_path=".env")
    db_name: str = os.getenv("CLAN_BATTLE_DB_NAME")
    db: database.Database = get_db(db_name)
    if db is None:
        raise DatabaseError("Failed to get database.")
    print("Database connected successfully.")

    clan_totals: List[apiClanTotal] = get_clan_totals()
    if not clan_totals:
        raise ClanError("Failed to get clan totals.")
    print("Clan totals fetched successfully.")

    clans: List[apiClan] = []
    for clan_total in clan_totals:
        clan: apiClan = get_clan(clan_name=clan_total.Name)
        if clan is not None:
            clans.append(clan)
        else:
            print(f"Failed to get clan: {clan_total.Name}")
    if not clans:
        raise ClanError("Failed to get clans.")
    print(f"{len(clans)} Clans fetched successfully.")

    for clan in clans:
        if not write_clan(clan=clan, db=db):
            raise DatabaseError(f"Failed to write clan {clan.Name}")

    print("Clans written successfully.")


if __name__ == "__main__":
    main()
