import time
from typing import List
from services import (
    get_clan_totals,
    get_clan,
    get_roblox_users_from_api,
    write_roblox_users,
    apiClan,
    apiClanTotal,
    RobloxUser,
)
from database import Client, get_db
from utils import clear_screen


class DatabaseError(Exception):
    pass


class ClanError(Exception):
    pass


class UserError(Exception):
    pass


def main():
    clear_screen()
    try:
        db: Client = get_db()
        if db is None:
            raise DatabaseError("Failed to get database.")
        print("Database connected successfully.")

        clan_totals: List[apiClanTotal] = get_clan_totals()
        if not clan_totals:
            raise ClanError("Failed to get clan totals.")
        print("Clan totals fetched successfully.")

        clan_names: List[str] = [clan.Name for clan in clan_totals]
        if not clan_names:
            raise ClanError("No clan names found.")
        print(f"{len(clan_names)} Clan names fetched successfully.")

        clans: List[apiClan] = []
        for clan_name in clan_names:
            clan: apiClan = get_clan(clan_name)
            if clan is not None:
                clans.append(clan)
            else:
                print(f"Failed to get clan: {clan_name}")
        if not clans:
            raise ClanError("Failed to get clans.")
        print(f"{len(clans)} Clans fetched successfully.")

        user_ids: List[int] = [
            member.UserID for clan in clans for member in clan.Members
        ]
        if not user_ids:
            raise UserError("No user IDs found.")
        print(f"{len(user_ids)} User IDs fetched successfully.")

        def fetch_users_in_chunks(user_ids: List[int]) -> List[RobloxUser]:
            user_data: List[RobloxUser] = []
            for i in range(0, len(user_ids), 100):
                chunk: List[int] = user_ids[i : i + 100]
                users: List[RobloxUser] = get_roblox_users_from_api(chunk)
                if not users:
                    raise UserError("Failed to get user data.")
                user_data.extend(users)
                print(
                    f"{len(user_data)}/{len(user_ids)} User data fetched successfully."
                )
                countdown_timer(25)

            return user_data

        def countdown_timer(seconds: int):
            for i in range(seconds, 0, -1):
                print(f"Sleeping for {i} seconds...", end="\r")
                time.sleep(1)
            print("")

        users: List[RobloxUser] = fetch_users_in_chunks(user_ids)
        if not users:
            raise UserError("Failed to get user data.")
        print(f"{len(users)} User data fetched successfully.")

        if not write_roblox_users(users, db):
            raise UserError("Failed to write user data.")

        print("User data written successfully.")

    except DatabaseError as e:
        print(f"DatabaseError: {e}")
        exit(1)


if __name__ == "__main__":
    main()
