import time
from datetime import date, datetime, timedelta
from typing import List

from config.config_utils import get_managed_leagues_config, get_managed_teams_config
from src.api.fixtures_client import FixturesClient
from src.db.fixtures_db_manager import FixturesDBManager
from src.entities import Fixture, FixtureForDB
from src.notifier_logger import get_logger
from src.utils.date_utils import get_formatted_date, is_time_in_surrounding_hours
from src.utils.fixtures_utils import (
    convert_fixture_response_to_db_fixture,
    convert_fixtures_response_to_db,
)

FIXTURES_DB_MANAGER = FixturesDBManager()
MANAGED_TEAMS = get_managed_teams_config()
MANAGED_LEAGUES = get_managed_leagues_config()
FIXTURES_CLIENT = FixturesClient()

logger = get_logger(__name__)


def get_converted_fixtures_to_db(fixtures: List[Fixture]) -> List[FixtureForDB]:
    converted_fixtures = []
    fix_nr = 1
    for fixture in fixtures:
        fixture_match = (
            f'{fixture["teams"]["home"]["name"]} vs. '
            f'{fixture["teams"]["away"]["name"]}'
        )
        logger.info(
            f"Converting & populating fixture {fix_nr}/"
            f"{len(fixtures)} - {fixture_match}"
        )
        fix_nr += 1

    return converted_fixtures


def populate_managed_teams() -> None:
    for team in MANAGED_TEAMS:
        FIXTURES_DB_MANAGER.insert_managed_team(team)


def populate_managed_leagues() -> None:
    for league in MANAGED_LEAGUES:
        FIXTURES_DB_MANAGER.insert_managed_league(league)


def populate_team_fixtures(is_initial) -> None:
    current_year = date.today().year
    last_year = current_year - 1

    for team in MANAGED_TEAMS:
        if is_initial:
            logger.info(f"Saving fixtures for team {team.name} - season {last_year}")
            populate_single_team_fixture(team.id, last_year)

        logger.info(f"Saving fixtures for team {team.name} - season {current_year}")
        populate_single_team_fixture(team.id, current_year)
        # to avoid reaching rate limit at API calls.
        time.sleep(2.5)


def populate_single_team_fixture(team_id: int, season: int) -> None:
    team_fixtures = fixtures_client.get_fixtures_by(str(season), team_id)

    if "response" in team_fixtures.as_dict:
        FIXTURES_DB_MANAGER.save_fixtures(
            convert_fixtures_response_to_db(team_fixtures.as_dict["response"])
        )


def populate_single_league_fixture(
    league_id: int, season: str, between_dates: tuple
) -> None:
    league_fixtures = FIXTURES_CLIENT.get_fixtures_by(
        season, league_id=league_id, between_dates=between_dates
    )

    if "response" in league_fixtures.as_dict:
        FIXTURES_DB_MANAGER.save_fixtures(
            convert_fixtures_response_to_db(league_fixtures.as_dict["response"])
        )


def populate_league_fixtures() -> None:
    current_year = date.today().year
    today = datetime.today()
    yesterday_date = today + timedelta(days=-1)
    tomorrow_date = today + timedelta(weeks=10)
    from_date = yesterday_date.strftime("%Y-%m-%d")
    to_date = tomorrow_date.strftime("%Y-%m-%d")

    between_dates = (from_date, to_date)

    leagues = FIXTURES_DB_MANAGER.get_all_leagues()

    for league in leagues:
        logger.info(f"Saving fixtures for league {league.name}")

        populate_single_league_fixture(league.id, str(current_year), between_dates)

        # to avoid reaching rate limit at API calls.
        time.sleep(2.5)


def populate_data() -> None:
    populate_league_fixtures()


if __name__ == "__main__":
    logger.info("Populating data...")
    populate_data()
