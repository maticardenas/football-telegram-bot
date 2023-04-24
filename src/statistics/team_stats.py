from pydantic import BaseModel

from src.db.fixtures_db_manager import FixturesDBManager
from src.notifier_constants import NOT_PLAYED_OR_FINISHED_MATCH_STATUSES


class TeamRecord(BaseModel):
    games_won: int = 0
    games_drawn: int = 0
    games_lost: int = 0


class TeamStats:
    def __init__(self, team_id: int):
        self._fixtures_db_manager = FixturesDBManager()
        self._team_id = team_id

    def goals_scored_last_n_matches(self, number_of_matches: int) -> int:
        last_n_fixtures = self._fixtures_db_manager.get_last_fixture(
            team_id=self._team_id, number_of_fixtures=number_of_matches
        )
        return sum(
            fixture.home_score
            if fixture.home_team == self._team_id
            else fixture.away_score
            for fixture in last_n_fixtures
        )

    def goals_received_last_n_matches(self, number_of_matches: int) -> int:
        last_n_fixtures = self._fixtures_db_manager.get_last_fixture(
            team_id=self._team_id, number_of_fixtures=number_of_matches
        )
        return sum(
            fixture.home_score
            if fixture.home_team != self._team_id
            else fixture.away_score
            for fixture in last_n_fixtures
        )

    def team_record_in_last_n_matches(self, number_of_matches: int) -> dict:
        last_n_fixtures = self._fixtures_db_manager.get_last_fixture(
            team_id=self._team_id, number_of_fixtures=number_of_matches
        )
        games_won = 0
        games_drawn = 0
        games_lost = 0

        for fixt in last_n_fixtures:
            if (
                fixt.match_status in NOT_PLAYED_OR_FINISHED_MATCH_STATUSES
                or "half" in fixt.match_status
            ):
                continue

            if fixt.home_team == self._team_id:
                if fixt.home_score > fixt.away_score:
                    games_won += 1
                elif fixt.home < fixt.fixt.away_score:
                    games_lost += 1
                else:
                    games_drawn += 1
            else:
                if fixt.home_score > fixt.away_score:
                    games_lost += 1
                elif fixt.home < fixt.fixt.away_score:
                    games_won += 1
                else:
                    games_drawn += 1

        return TeamRecord(games_won, games_drawn, games_lost)
