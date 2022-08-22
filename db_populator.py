import time
from datetime import date, datetime, timedelta
from typing import List

from src.api.fixtures_client import FixturesClient
from src.db.fixtures_db_manager import FixturesDBManager
from src.entities import Fixture, FixtureForDB
from src.notifier_logger import get_logger
from src.utils.fixtures_utils import convert_fixtures_response_to_db
from src.utils.fixtures_utils import (
    convert_fixtures_response_to_db,
)

FIXTURES_DB_MANAGER = FixturesDBManager()
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


def populate_single_team_fixture(team_id: int, season: int) -> None:
    team_fixtures = FIXTURES_CLIENT.get_fixtures_by(str(season), team_id)

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

def get_leagues_to_update():
    initial_leagues = FIXTURES_DB_MANAGER.get_all_leagues(daily_update=True)
    initial_leagues_ids = [league.id for league in initial_leagues]
    favourite_leagues = FIXTURES_DB_MANAGER.get_all_favourite_leagues()

    leagues_to_update = []

    for fv_league in favourite_leagues:
        if fv_league in initial_leagues_ids:
            continue
        else:
            leagues_to_update.append(FIXTURES_DB_MANAGER.get_league(fv_league.id)[0])

    return leagues_to_update


def populate_league_fixtures() -> None:
    current_year = date.today().year
    today = datetime.today()
    yesterday_date = today + timedelta(days=-1)
    tomorrow_date = today + timedelta(weeks=10)
    from_date = yesterday_date.strftime("%Y-%m-%d")
    to_date = tomorrow_date.strftime("%Y-%m-%d")

    between_dates = (from_date, to_date)

    leagues = get_leagues_to_update()

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
