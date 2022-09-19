from datetime import datetime
from typing import List

from src.api.fixtures_client import FixturesClient
from src.db.fixtures_db_manager import FixturesDBManager
from src.notifier_logger import get_logger
from src.utils.date_utils import get_formatted_date, is_time_in_surrounding_hours
from src.utils.fixtures_utils import (
    convert_fixture_response_to_db_fixture,
    convert_fixtures_response_to_db,
)

FIXTURES_DB_MANAGER = FixturesDBManager()
FIXTURES_CLIENT = FixturesClient()

logger = get_logger(__name__)


def update_fixtures() -> None:
    """
    This function updates only fixtures which are in surrounding current time for certain number of hours.
    """
    fixtures_client = FixturesClient()
    fixtures_to_update = get_all_fixtures_ids_to_update()
    lots_to_update = list(get_fixture_update_lots(fixtures_to_update))

    for lot in lots_to_update[:1]:
        logger.info(f"Updating fixtures for lot {lot}")
        team_fixtures = fixtures_client.get_fixtures_by(ids=lot)
        FIXTURES_DB_MANAGER.save_fixtures(
            convert_fixtures_response_to_db(team_fixtures.as_dict["response"])
        )


def get_fixture_update_lots(
    fixtures_to_update: List[int], lot_size: int = 20
) -> List[List[int]]:
    for i in range(0, len(fixtures_to_update), lot_size):
        yield fixtures_to_update[i : i + lot_size]


def get_all_fixtures_ids_to_update() -> List["DBFixture"]:
    todays_fixtures = FIXTURES_DB_MANAGER.get_games_in_surrounding_n_hours(
        3, favourite=True
    )

    return [fixture.id for fixture in todays_fixtures if fixture]


def populate_surrounding_fixtures() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    fixtures_response = FIXTURES_CLIENT.get_fixtures_by(date=today)

    for item in fixtures_response.as_dict.get("response", []):
        if isinstance(item, list):
            for fixture in item:
                # check_time = get_formatted_date(fixture["fixture"]["date"]).time()
                # if is_time_in_surrounding_hours(check_time, hours=3):
                FIXTURES_DB_MANAGER.save_fixtures(
                    [convert_fixture_response_to_db_fixture(fixture)]
                )
        else:
            # check_time = get_formatted_date(item["fixture"]["date"]).time()
            # if is_time_in_surrounding_hours(check_time, hours=3):
            FIXTURES_DB_MANAGER.save_fixtures(
                [convert_fixture_response_to_db_fixture(item)]
            )


if __name__ == "__main__":
    populate_surrounding_fixtures()
