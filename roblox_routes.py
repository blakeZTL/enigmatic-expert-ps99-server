from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from typing import List
from models import RobloxUser, RobloxUserWithUsername

router = APIRouter()


@router.get(
    "/",
    response_description="List all roblox users",
    response_model=List[RobloxUser],
)
async def list_roblox_users(request: Request):
    users = (
        await request.app.mongodb_client["roblox"]["users"]
        .find({})
        .to_list(length=None)
    )
    return users


@router.get(
    "/{id}",
    response_description="Get a single roblox user",
    response_model=RobloxUser,
)
async def show_roblox_user(id: int, request: Request):
    if (
        user := request.app.mongodb_client["roblox"]["users"].find_one({"_id": id})
    ) is not None:
        return user

    raise HTTPException(status_code=404, detail=f"Roblox user {id} not found")


@router.get(
    "/username/{username}",
    response_description="Get a single roblox user by username",
    response_model=RobloxUserWithUsername,
)
async def show_roblox_user_by_username(username: str, request: Request):
    url = f"https://users.roblox.com/v1/usernames/users"
    body = {"usernames": [username], "excludeBannedUsers": True}
    response = await request.app.http_client.post(url, json=body)
    print(f"response: {response}")
    if response.status_code == 200:
        data = response.json()
        if data and "data" in data and data["data"]:
            user = data["data"][0]
            return user
        raise HTTPException(status_code=404, detail=f"Roblox user {username} not found")

    raise HTTPException(
        status_code=404, detail=f"Error retrieving roblox user {username}"
    )
