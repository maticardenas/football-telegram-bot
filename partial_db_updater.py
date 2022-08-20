from typing import List

from config.config_utils import get_managed_teams_config
from src.api.fixtures_client import FixturesClient
from src.db.fixtures_db_manager import FixturesDBManager
from src.notifier_logger import get_logger
from src.utils.fixtures_utils import convert_fixtures_response_to_db

FIXTURES_DB_MANAGER = FixturesDBManager()
MANAGED_TEAMS = get_managed_teams_config()

logger = get_logger(__name__)


def update_fixtures() -> None:
    """
    This function updates only fixtures corresponding to the
    last & next match for each managed team, given that this is
    at the moment the only that the user can query, doesn't make sense to
    query all the fixtures for all teams. This way we can save dozens of
    RAPID API hits per day, giving space to multiple other functionalities.
    """
    fixtures_client = FixturesClient()
    fixtures_to_update = get_all_fixtures_ids_to_update()
    lots_to_update = get_fixture_update_lots(fixtures_to_update)

    for lot in lots_to_update:
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
    todays_fixtures = FIXTURES_DB_MANAGER.get_games_in_surrounding_n_hours(2)

    return [fixture.id for fixture in todays_fixtures if fixture]


if __name__ == "__main__":
    update_fixtures()
