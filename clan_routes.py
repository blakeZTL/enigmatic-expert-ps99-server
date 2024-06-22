from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from typing import List
from models import Clan

router = APIRouter()


def clan_helper(clan) -> Clan:
    return Clan(
        id=str(clan["_id"]),
        Owner=clan["Owner"],
        Name=clan["Name"],
        Icon=clan["Icon"],
        Desc=clan["Desc"],
        Members=clan["Members"],
        DepositedDiamonds=clan["DepositedDiamonds"],
        DiamondContributions=clan["DiamondContributions"],
        Status=clan["Status"],
        Battles=clan["Battles"],
    )


@router.get(
    "/",
    response_description="List all clan data",
    response_model=List[Clan],
)
async def list_clans(request: Request):
    clan_records = request.app.mongodb_client["clan-battles"]["clans"].find({})
    return clan_records


@router.get(
    "/{clan_name}",
    response_description="Get clan records by clan name",
    response_model=List[Clan],
)
async def show_clan_records(clan_name: str, request: Request):
    print(f"show_clan_records({clan_name})")
    clan_records = (
        await request.app.mongodb_client["clan-battles"]["clans"]
        .find({"Name": clan_name})
        .to_list(length=None)
    )
    if clan_records is not None:
        clans = []
        for clan in clan_records:
            clans.append(clan_helper(clan))
        return clans

    raise HTTPException(status_code=404, detail=f"Clan record {clan_name} not found")
