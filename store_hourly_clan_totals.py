from typing import List
from services import (
    get_clan_totals,
    write_clan_totals,
    apiClanTotal,
)
from database import Client, get_db


class DatabaseError(Exception):
    pass


class ClanError(Exception):
    pass


def main():
    db: Client = get_db()
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
