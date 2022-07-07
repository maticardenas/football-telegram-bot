from datetime import date, datetime, timedelta
from typing import List

from config.config_utils import get_managed_teams_config, get_managed_leagues_config
from src.api.fixtures_client import FixturesClient
from src.db.fixtures_db_manager import FixturesDBManager
from src.entities import Fixture, FixtureForDB
from src.notifier_logger import get_logger
from src.utils.fixtures_utils import convert_fixture_response_to_db

FIXTURES_DB_MANAGER = FixturesDBManager()
MANAGED_TEAMS = get_managed_teams_config()
MANAGED_LEAGUES = get_managed_leagues_config()

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
        converted_fixtures.append(convert_fixture_response_to_db(fixture))
        fix_nr += 1

    return converted_fixtures


def populate_managed_teams() -> None:
    for team in MANAGED_TEAMS:
        FIXTURES_DB_MANAGER.insert_managed_team(team)


def populate_managed_leagues() -> None:
    for league in MANAGED_LEAGUES:
        FIXTURES_DB_MANAGER.insert_managed_league(league)


def populate_team_fixtures(is_initial) -> None:
    fixtures_client = FixturesClient()
    current_year = date.today().year
    last_year = current_year - 1

    for team in MANAGED_TEAMS:
        logger.info(f"Saving fixtures for team {team.name}")

        if is_initial:
            team_fixtures = fixtures_client.get_fixtures_by(str(last_year), team.id)
            if "response" in team_fixtures.as_dict:
                FIXTURES_DB_MANAGER.save_fixtures(
                    get_converted_fixtures_to_db(team_fixtures.as_dict["response"])
                )

        team_fixtures = fixtures_client.get_fixtures_by(str(current_year), team.id)
        if "response" in team_fixtures.as_dict:
            FIXTURES_DB_MANAGER.save_fixtures(
                get_converted_fixtures_to_db(team_fixtures.as_dict["response"])
            )


def populate_league_fixtures() -> None:
    fixtures_client = FixturesClient()
    current_year = date.today().year
    today = datetime.today()
    yesterday_date = today + timedelta(days=-1)
    tomorrow_date = today + timedelta(days=1)
    from_date = yesterday_date.strftime("%Y-%m-%d")
    to_date = tomorrow_date.strftime("%Y-%m-%d")

    between_dates = (from_date, to_date)

    for league in MANAGED_LEAGUES:
        logger.info(f"Saving fixtures for league {league.name}")

        league_fixtures = fixtures_client.get_fixtures_by(
            str(current_year), league_id=league.id, between_dates=between_dates
        )

        if "response" in league_fixtures.as_dict:
            FIXTURES_DB_MANAGER.save_fixtures(
                get_converted_fixtures_to_db(league_fixtures.as_dict["response"])
            )


def populate_data(is_initial=False) -> None:
    populate_managed_teams()
    populate_managed_leagues()
    populate_team_fixtures(is_initial)
    populate_league_fixtures()


if __name__ == "__main__":
    logger.info("Populating data...")
    fixtures = FIXTURES_DB_MANAGER.get_all_fixtures()
    is_initial = True if not len(fixtures) else False

    logger.info(f"IS_INITIAL -> {is_initial}")

    populate_data(is_initial)
