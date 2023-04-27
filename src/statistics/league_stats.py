from pydantic import BaseModel

from src.db.fixtures_db_manager import FixturesDBManager
from src.notifier_constants import NOT_PLAYED_OR_FINISHED_MATCH_STATUSES


class LeagueStats:
    def __init__(self, league_id: int) -> None:
        self._fixtures_db_manager = FixturesDBManager()
        self._league_id = league_id

    def goals_scored_last_n_matches(self, number_of_matches: int) -> int:
        last_n_fixtures = self._fixtures_db_manager.get_last_fixture(
            league_id=self._league_id, number_of_fixtures=number_of_matches
        )
        return sum(
            fixture.home_score + fixture.away_score for fixture in last_n_fixtures
        )
