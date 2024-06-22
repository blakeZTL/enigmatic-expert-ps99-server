import os
# import json
# import base64
from dotenv import load_dotenv
import pymongo
import pymongo.database
# import firebase_admin
# from firebase_admin import credentials, firestore
# from google.cloud.firestore import Client
# from firebase_admin.credentials import Certificate



load_dotenv(dotenv_path=".env")

def get_db(database:str)->pymongo.database.Database:    
    connection_str:str = os.getenv('MONGO_DB_CONNECTION_STRING')
    if connection_str is None:
        print("MONGO_DB_CONNECTION_STRING not found in .env file")
        return None
    client: pymongo.MongoClient = pymongo.MongoClient(connection_str)
    db: pymongo.database.Database = client[database]
    return db


    # encoded_json_str = os.getenv('SERVICE_ACCOUNT')
    # json_data = None
    # if encoded_json_str:
    #     try:
    #         decoded_json_str = base64.b64decode(encoded_json_str).decode()
    #         json_data = json.loads(decoded_json_str)
    #     except Exception as e:
    #         print(f"Error decoding and parsing JSON: {e}")
    # else:
    #     print("SERVICE_ACCOUNT not found in .env file")

    # if json_data is None:
    #     return None

    # cred: Certificate = credentials.Certificate(json_data)
    # firebase_admin.initialize_app(cred)
    # db: Client = firestore.client()

    # return db

if __name__ == "__main__":
    db = get_db("roblox")
    if db is None:
        print("Failed to get database.")
    else:
        print("Database connected successfully.")
