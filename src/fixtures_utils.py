from datetime import datetime
from typing import Any, Dict, List

from src.entities import Fixture


def get_champions_league_fixtures(all_team_fixtures: Dict[str, Any]) -> List[Dict[str, str]]:
    return [
        fixture for fixture in all_team_fixtures["response"]
        if fixture["league"]["id"] == 2
    ]

def date_diff(date: str) -> float:
    return (datetime.strptime(date[:-6], "%Y-%m-%dT%H:%M:%S") - datetime.now()).days

def get_next_fixture(team_fixtures: List[Dict[str, Any]]) -> Dict[str, Any]:
    min_fixture = None
    min_diff = 9999

    for fixture in team_fixtures:
        fixture_date_diff = date_diff(fixture["fixture"]["date"])

        if not min_fixture and fixture_date_diff >= 0:
            min_fixture = fixture
            min_diff = fixture_date_diff

        if fixture_date_diff >= 0 and (fixture_date_diff < min_diff):
            min_diff = fixture_date_diff
            min_fixture = fixture

    return __convert_fixture_response(min_fixture)


def __convert_fixture_response(fixture_response: Dict[str, Any]) -> Fixture:
    return Fixture(
        fixture_response["fixture"]["date"],
        fixture_response["fixture"]["referee"],
        fixture_response["fixture"]["status"]["long"],
        fixture_response["league"]["name"],
        fixture_response["league"]["round"],
        fixture_response["teams"]["home"]["name"],
        fixture_response["teams"]["away"]["name"],
    )
