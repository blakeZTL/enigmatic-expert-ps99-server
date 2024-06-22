from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import RobloxUser

router = APIRouter()


@router.get(
    "/",
    response_description="List all roblox users",
    response_model=List[RobloxUser],
)
async def list_roblox_users(request: Request):
    users = request.app.mongodb_client["roblox"]["users"].find({})
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


# @router.post(
#     "/",
#     response_description="Add new roblox user",
#     response_model=RobloxUser,
#     status_code=status.HTTP_201_CREATED,
# )
# async def create_roblox_user(request: Request, user: RobloxUser = Body(...)):
#     user = jsonable_encoder(user)
#     new_user = request.app.mongodb_client["roblox"]["users"].insert_one(user)
#     created_user = request.app.mongodb_client["roblox"]["users"].find_one(
#         {"_id": new_user.inserted_id}
#     )
#     return created_user
