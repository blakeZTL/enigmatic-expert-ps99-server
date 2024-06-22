from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import ClanTotal

router = APIRouter()


@router.get(
    "/clan-totals",
    response_description="List all clan totals",
    response_model=List[ClanTotal],
)
async def list_clan_totals(request: Request):
    clan_totals = request.app.mongodb_client["clan-battles"]["clan-totals"].find({})
    return clan_totals


@router.get(
    "/clan-totals/{id}",
    response_description="Get a single clan total",
    response_model=ClanTotal,
)
async def show_clan_total(id: str, request: Request):
    if (
        clan_total := request.app.mongodb_client["clan-battles"][
            "clan-totals"
        ].find_one({"_id": id})
    ) is not None:
        return clan_total

    raise HTTPException(status_code=404, detail=f"Clan total {id} not found")


# @router.post(
#     "/",
#     response_description="Add new clan total",
#     response_model=ClanTotal,
#     status_code=status.HTTP_201_CREATED,
# )
# async def create_clan_total(request: Request, clan_total: ClanTotal = Body(...)):
#     clan_total = jsonable_encoder(clan_total)
#     new_clan_total = request.app.database["clan_totals"].insert_one(clan_total)
#     created_clan_total = request.app.database["clan_totals"].find_one(
#         {"_id": new_clan_total.inserted_id}
#     )
#     return created_clan_total
