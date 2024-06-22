import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from roblox_routes import router as roblox_routes
from clan_total_routes import router as clan_total_routes
from clan_routes import router as clan_routes
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

origins = [
    "https://hidden-caverns-01384-1c5c4dad7960.herokuapp.com",
    "http://www.ps99clanbattlestats.com",
    "https://www.ps99clanbattlestats.com",
    "http://www.ps99clanbattlestats.io",
    "https://www.ps99clanbattlestats.io",
    "ps99clanbattlestats.com",
    "ps99clanbattlestats.io",
    "http://localhost:5173",
    "http://localhost:8000",
]


config = dotenv_values(".env")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    server_app.mongodb_client = AsyncIOMotorClient(config["ATLAS_URI"])
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

server_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
