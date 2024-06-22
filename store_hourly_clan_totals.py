from typing import List
import os
from services import (
    get_clan_totals,
    write_clan_totals,
    apiClanTotal,
)
from database import get_db
from pymongo import database
from dotenv import load_dotenv


class DatabaseError(Exception):
    pass


class ClanError(Exception):
    pass


def main():
    load_dotenv(dotenv_path=".env")
    db_name:str = os.getenv('PS99_CLAN_BATTLE_DB_NAME')
    db: database.Database = get_db(db_name)
    if db is None:
        raise DatabaseError("Failed to get database.")
    print("Database connected successfully.")

    clan_totals: List[apiClanTotal] = get_clan_totals()
    if not clan_totals:
        raise ClanError("Failed to get clan totals.")
    print("Clan totals fetched successfully.")

    if not write_clan_totals(clan_totals=clan_totals, db=db):
        raise DatabaseError("Failed to write clan totals.")

    print("Clan totals written successfully.")


if __name__ == "__main__":
    main()
