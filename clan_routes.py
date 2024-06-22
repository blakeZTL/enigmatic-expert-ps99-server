from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Clan

router = APIRouter()


@router.get(
    "/clans",
    response_description="List all clan data",
    response_model=List[Clan],
)
async def list_clans(request: Request):
    clan_totals = request.app.mongodb_client["clan-battles"]["clans"].find({})
    return clan_totals


@router.get(
    "/clans/{id}",
    response_description="Get a single clan record",
    response_model=Clan,
)
async def show_clan_record(id: str, request: Request):
    if (
        clan_total := request.app.mongodb_client["clan-battles"]["clans"].find_one(
            {"_id": id}
        )
    ) is not None:
        return clan_total

    raise HTTPException(status_code=404, detail=f"Clan record {id} not found")
