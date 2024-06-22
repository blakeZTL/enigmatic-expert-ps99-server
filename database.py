import os
from dotenv import load_dotenv
import pymongo
import pymongo.database


load_dotenv(dotenv_path=".env")


def get_db(database: str) -> pymongo.database.Database:
    connection_str: str = os.getenv("ATLAS_URI")
    if connection_str is None:
        print("ATLAS_URI not found in .env file")
        return None
    client: pymongo.MongoClient = pymongo.MongoClient(connection_str)
    db: pymongo.database.Database = client[database]
    return db


if __name__ == "__main__":
    db = get_db("roblox")
    if db is None:
        print("Failed to get database.")
    else:
        print("Database connected successfully.")
