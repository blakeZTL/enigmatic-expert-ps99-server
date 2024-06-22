from typing import List
from pydantic import BaseModel, Field


class RobloxUser(BaseModel):
    id: int = Field(alias="_id")
    hasVerifiedBadge: bool
    name: str
    displayName: str

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": 1,
                "hasVerifiedBadge": True,
                "name": "test",
                "displayName": "Test",
            }
        }


class ClanTotal(BaseModel):
    id: str = Field(alias="_id")
    Name: str
    DepositedDiamonds: int
    Members: int
    Points: int

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "ClanName||2021-01-01T00:00:00.000000",
                "Name": "ClanName",
                "DepositedDiamonds": 1,
                "Members": 1,
                "Points": 1,
            }
        }


class ClanMember(BaseModel):
    UserID: int
    PermissionLevel: int
    JoinTime: int

    class Config:
        json_schema_extra = {
            "example": {
                "UserID": 1,
                "PermissionLevel": 1,
                "JoinTime": 1,
            }
        }


class DiamondContribution(BaseModel):
    UserID: int
    Diamonds: int

    class Config:
        json_schema_extra = {
            "example": {
                "UserID": 1,
                "Diamonds": 1,
            }
        }


class ClanParticipation(BaseModel):
    UserID: int
    Points: int

    class Config:
        json_schema_extra = {
            "example": {
                "UserID": 1,
                "Points": 1,
            }
        }


class ClanBattle(BaseModel):
    BattleID: str
    Points: int
    PointContributions: List[ClanParticipation]
    EarnedMedal: str

    class Config:
        json_schema_extra = {
            "example": {
                "BattleID": "BattleName",
                "Points": 1,
                "PointContributions": [
                    {
                        "UserID": 1,
                        "Points": 1,
                    }
                ],
                "EarnedMedal": "Gold",
            }
        }


class Clan(BaseModel):
    id: str = Field(alias="_id")
    Owner: int
    Name: str
    Icon: str
    Desc: str
    Members: List[ClanMember]
    DepositedDiamonds: int
    DiamondContributions: List[DiamondContribution]
    Status: str
    Battles: List[ClanBattle]

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "ClanName||2021-01-01T00:00:00.000000",
                "Owner": 1,
                "Name": "ClanName",
                "Icon": "https://www.roblox.com/asset/?id=1",
                "Desc": "Clan description",
                "Members": [
                    {
                        "UserID": 1,
                        "PermissionLevel": 1,
                        "JoinTime": 1,
                    }
                ],
                "DepositedDiamonds": 1,
                "DiamondContributions": [
                    {
                        "UserID": 1,
                        "Diamonds": 1,
                    }
                ],
                "Status": "Active",
                "Battles": [
                    {
                        "BattleID": "BattleName",
                        "Points": 1,
                        "PointContributions": [
                            {
                                "UserID": 1,
                                "Points": 1,
                            }
                        ],
                        "EarnedMedal": "Gold",
                    }
                ],
            }
        }
