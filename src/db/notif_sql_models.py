from typing import List, Optional

from sqlmodel import Field, SQLModel


class League(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int = Field(primary_key=True)
    name: str
    country: str
    logo: str
    daily_season_fixt_update: str


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
    bsas_date: str
    league: int = Field(foreign_key="league.id")
    round: str
    home_team: int = Field(foreign_key="team.id")
    away_team: int = Field(foreign_key="team.id")
    venue: str
    match_status: str
    referee: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    highlights: Optional[List[str]]


class FavouriteTeam(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    chat_id: str = Field(primary_key=True)
    team: int = Field(foreign_key="team.id", primary_key=True)


class FavouriteLeague(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    chat_id: str = Field(primary_key=True)
    league: int = Field(foreign_key="league.id", primary_key=True)


class TimeZone(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    emoji: str = ""
