import copy
from datetime import datetime

import pytest

from src.entities import Fixture, Team, Championship, MatchScore
from src.utils.date_utils import get_time_in_time_zone, TimeZones

@pytest.fixture
def team() -> Team:
    return Team(
        id=435,
        name="River Plate",
        picture="https://media.api-sports.io/football/teams/435.png",
        aliases={}
    )

@pytest.fixture
def league() -> Championship:
    return Championship(
        league_id=483,
        name="Copa de la Superliga",
        country="Argentina",
        logo="https://media.api-sports.io/football/leagues/483.png"
    )

@pytest.fixture
def match_score() -> MatchScore:
    return MatchScore(
        home_score=3,
        away_score=0
    )

@pytest.fixture
def fixture(team: Team, league: Championship, match_score: MatchScore) -> Fixture:
    utc_date = datetime.strptime("2019-01-01T15:00:00", "%Y-%m-%dT%H:%M:%S")
    bsas_date = get_time_in_time_zone(utc_date, TimeZones.BSAS)
    ams_date = get_time_in_time_zone(utc_date, TimeZones.AMSTERDAM)

    away_team = copy.deepcopy(team)
    away_team.name = "Boca Juniors"
    away_team.id = 451

    return Fixture(
        id=345345,
        utc_date=utc_date,
        bsas_date=bsas_date,
        ams_date=ams_date,
        date_diff=1,
        referee="Perluigi Colina",
        match_status="Started",
        championship=league,
        round="Primera Fecha",
        home_team=team,
        away_team=away_team,
        match_score=match_score
    )