from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, SQLModel


class League(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int = Field(primary_key=True)
    name: str
    country: str
    logo: str


class Team(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int = Field(primary_key=True)
    name: str
    picture: str
    aliases: Optional[List[str]]


class Fixture(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int = Field(primary_key=True)
    utc_date: str
    league: int = Field(foreign_key="league.id")
    round: str
    home_team: int = Field(foreign_key="team.id")
    away_team: int = Field(foreign_key="team.id")
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    highlights: Optional[List[str]]
