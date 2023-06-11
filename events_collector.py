from typing import List

from src.api.fixtures_client import FixturesClient
from src.db.fixtures_db_manager import FixturesDBManager
from src.entities import Event
from src.notifier_logger import get_logger

FIXTURES_DB_MANAGER = FixturesDBManager()
FIXTURES_CLIENT = FixturesClient(
    share_session=True, raise_for_status=True, perform_retries=True
)

logger = get_logger(__name__)


def collect_events() -> None:
    """
    This functions collects and insert all events into a database.
    """
    fixtures_client = FixturesClient()
    fixtures_to_collect = get_all_fixtures_ids_to_collect_events()

    for fixture_id in fixtures_to_collect:
        events_response = fixtures_client.get_events(fixture_id)
        for fixt_event in events_response.as_dict.get("response", []):
            event = Event(**fixt_event)
            event.fixture_id = fixture_id
            FIXTURES_DB_MANAGER.save_fixture_event(event)


def is_from_favourite_league_or_has_favourite_teams(fixture) -> bool:
    all_favourite_teams = FIXTURES_DB_MANAGER.get_all_favourite_teams()

    return (
        fixture.league not in FIXTURES_DB_MANAGER.get_all_favourite_leagues()
        and fixture.home_team not in all_favourite_teams
        and fixture.away_team not in all_favourite_teams
    )


def get_all_fixtures_ids_to_collect_events() -> List[int]:
    surrounding = FIXTURES_DB_MANAGER.get_games_in_surrounding_n_hours(
        hours=-5, favourite=True, status="finished"
    )

    filtered_fixtures_ids = []

    for fixture in surrounding:
        fixture_events = FIXTURES_DB_MANAGER.get_fixture_events(fixture.id)

        if len(fixture_events):
            logger.info(
                f"Events for fixture {fixture.id} ({fixture.home_team} vs. {fixture.away_team}) were already collected."
            )
            continue

        filtered_fixtures_ids.append(fixture.id)

    return filtered_fixtures_ids


if __name__ == "__main__":
    collect_events()
