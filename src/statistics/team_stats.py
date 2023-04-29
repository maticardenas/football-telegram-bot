from typing import Optional

from pydantic import BaseModel, validator

from src.db.fixtures_db_manager import FixturesDBManager
from src.emojis import Emojis
from src.notifier_constants import NOT_PLAYED_OR_FINISHED_MATCH_STATUSES


class TeamRecord(BaseModel):
    games_won: int = 0
    games_drawn: int = 0
    games_lost: int = 0
    games_played: int = 0
    all_record_matches_emojis: str = ""
    overall_emoji: str = ""

    @validator("overall_emoji", always=True, pre=True)
    def set_emoji(cls, v, values, **kwargs):
        games_won = values.get("games_won", 0)
        games_drawn = values.get("games_drawn", 0)
        games_lost = values.get("games_lost", 0)

        if games_won > games_lost:
            if games_won >= games_drawn:
                return Emojis.SMILEY_FACE.value
            else:
                return Emojis.FACE_WITHOUT_MOUTH.value
        elif games_won == games_lost:
            return Emojis.FACE_WITHOUT_MOUTH.value
        else:
            return Emojis.SAD_FACE.value

    @validator("games_played", always=True, pre=True)
    def set_games_played(cls, v, values, **kwargs):
        games_won = values.get("games_won", 0)
        games_drawn = values.get("games_drawn", 0)
        games_lost = values.get("games_lost", 0)

        return games_won + games_drawn + games_lost


class TeamStats:
    def __init__(self, team_id: int):
        self._fixtures_db_manager = FixturesDBManager()
        self._team_id = team_id

    def number_of_goals(
        self,
        number_of_matches: int = 5,
        scored: bool = True,
        year: Optional[str] = None,
    ):
        last_n_fixtures = self._fixtures_db_manager.get_last_fixture(
            team_id=self._team_id, number_of_fixtures=number_of_matches, year=year
        )

        number_of_goals = 0

        for fixture in last_n_fixtures:
            if (
                fixture.match_status in NOT_PLAYED_OR_FINISHED_MATCH_STATUSES
                or "half" in fixture.match_status
                or fixture.home_score is None
                or fixture.away_score is None
            ):
                continue

            if fixture.home_team == self._team_id:
                number_of_goals = (
                    number_of_goals + fixture.home_score
                    if scored
                    else number_of_goals + fixture.away_score
                )
            else:
                number_of_goals = (
                    number_of_goals + fixture.away_score
                    if scored
                    else number_of_goals + fixture.home_score
                )

        return number_of_goals

    def team_record_in_last_n_matches(
        self, number_of_matches: int, year: Optional[str] = None
    ) -> TeamRecord:
        last_n_fixtures = self._fixtures_db_manager.get_last_fixture(
            team_id=self._team_id, number_of_fixtures=number_of_matches, year=year
        )
        games_won = 0
        games_drawn = 0
        games_lost = 0
        record_emojis = []

        for fixt in last_n_fixtures:
            if (
                fixt.match_status in NOT_PLAYED_OR_FINISHED_MATCH_STATUSES
                or "half" in fixt.match_status
                or fixt.home_score is None
                or fixt.away_score is None
            ):
                continue

            if fixt.home_team == self._team_id:
                if fixt.home_score > fixt.away_score:
                    games_won += 1
                    record_emojis.append(Emojis.CHECK_MARK_BUTTON.value)
                elif fixt.home_score < fixt.away_score:
                    games_lost += 1
                    record_emojis.append(Emojis.CROSS_MARK.value)
                else:
                    games_drawn += 1
                    record_emojis.append(Emojis.EQUAL.value)
            else:
                if fixt.home_score > fixt.away_score:
                    games_lost += 1
                    record_emojis.append(Emojis.CROSS_MARK.value)
                elif fixt.home_score < fixt.away_score:
                    games_won += 1
                    record_emojis.append(Emojis.CHECK_MARK_BUTTON.value)
                else:
                    games_drawn += 1
                    record_emojis.append(Emojis.EQUAL.value)

        return TeamRecord(
            games_won=games_won,
            games_drawn=games_drawn,
            games_lost=games_lost,
            all_record_matches_emojis="".join(record_emojis),
        )
