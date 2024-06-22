from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from typing import List
from models import RobloxUser

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
