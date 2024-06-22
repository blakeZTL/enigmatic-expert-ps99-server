from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from roblox_routes import router as roblox_routes
from clan_total_routes import router as clan_total_routes
from clan_routes import router as clan_routes

config = dotenv_values(".env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    server_app.mongodb_client = MongoClient(config["ATLAS_URI"])
    print("Connected to the MongoDB database!")
    yield
    print("Closing the MongoDB database connection.")
    server_app.mongodb_client.close()


server_app = FastAPI(lifespan=lifespan)


server_app.include_router(roblox_routes, tags=["roblox"], prefix="/roblox-users")
server_app.include_router(
    clan_total_routes, tags=["clan-totals"], prefix="/clan-totals"
)
server_app.include_router(clan_routes, tags=["clans"], prefix="/clans")
