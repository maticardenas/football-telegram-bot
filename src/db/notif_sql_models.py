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
    country: int = Field(foreign_key="country.id")
    aliases: Optional[List[str]]


class Country(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int = Field(primary_key=True)
    name: str


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
    played_notified: bool = False
    approach_notified: bool = False
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    penalty_home_score: Optional[int] = None
    penalty_away_score: Optional[int] = None
    highlights: Optional[List[str]] = None


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


class UserTimeZone(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    chat_id: str = Field(primary_key=True)
    time_zone: int = Field(foreign_key="timezone.id", primary_key=True)
    is_main_tz: bool = False


class NotifType(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str


class NotifConfig(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    chat_id: int = Field(primary_key=True)
    notif_type: int = Field(foreign_key="notiftype.id", primary_key=True)
    status: bool = True
    time: str = ""


class Language(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    lang_id: int = Field(primary_key=True)
    name: str
    short_name: str


class ConfigLanguage(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    chat_id: str = Field(primary_key=True)
    lang_id: int = Field(foreign_key="language.lang_id", primary_key=True)


class Player(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int = Field(primary_key=True)
    name: str = ""


class Event(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    fixture: int = Field(foreign_key="fixture.id")
    time: int
    time_extra: Optional[str] = None
    team: int = Field(foreign_key="team.id")
    player: int = Field(default=None, foreign_key="player.id")
    assist: int = Field(default=None, foreign_key="player.id")
    type: str
    detail: Optional[str] = None
    comments: Optional[str] = None
