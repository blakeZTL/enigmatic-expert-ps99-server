from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import ClanTotal

router = APIRouter()


@router.get(
    "/",
    response_description="List all clan totals",
    response_model=List[ClanTotal],
)
async def list_clan_totals(request: Request):
    clan_totals = (
        await request.app.mongodb_client["clan-battles"]["clan-totals"]
        .find({})
        .to_list(length=None)
    )
    return clan_totals


@router.get(
    "/{id}",
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
