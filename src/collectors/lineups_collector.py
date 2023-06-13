import datetime
from typing import List

from src.api.fixtures_client import FixturesClient
from src.converters.converters import LineUpConverter
from src.db.fixtures_db_manager import FixturesDBManager
from src.db.line_ups_db_manager import LineUpsDBManager
from src.entities import Player
from src.notifier_logger import get_logger
from src.utils.date_utils import get_formatted_date

logger = get_logger(__name__)


class LineUpsCollector:
    def __init__(self):
        self._fixtures_client = FixturesClient(
            share_session=True, raise_for_status=True, perform_retries=True
        )
        self._fixtures_db_manager = FixturesDBManager()
        self._lines_ups_db_manager = LineUpsDBManager()

    def collect_line_ups(self) -> None:
        """
        This functions collects and insert all lineups into a database.
        """
        fixtures_to_collect = self.get_all_fixtures_ids_to_collect()

        for fixture_id in fixtures_to_collect:
            logger.info(f"Inserting line ups for fixture {fixture_id}")
            line_ups_response = self._fixtures_client.get_line_up(fixture_id)

            fixture = self._fixtures_db_manager.get_fixture_by_id(fixture_id)[0]

            fixture.line_up_check_attempt = (
                fixture.line_up_check_attempt + 1
                if fixture.line_up_check_attempt is not None
                else 1
            )
            self._fixtures_db_manager.insert_or_update_fixture(fixture)

            for team in line_ups_response.as_dict.get("response", []):
                team_id = team["team"]["id"]
                formation = team["formation"] if team["formation"] is not None else ""
                logger.info(f"Inserting line up for team {team_id}")

                for player in team["startXI"]:
                    converted_player_line_up = LineUpConverter().response_to_db_model(
                        fixture_id=fixture_id,
                        team_id=team_id,
                        formation=formation,
                        player_line_up_response=player["player"],
                    )
                    logger.info(
                        f"Inserting line up for player {converted_player_line_up.player} - #{converted_player_line_up.number} - {converted_player_line_up.pos} - {converted_player_line_up.grid}"
                    )

                    self._fixtures_db_manager.insert_player(
                        Player(
                            id=player["player"]["id"],
                            name=player["player"]["name"],
                        )
                    )
                    self._lines_ups_db_manager.insert_line_up(converted_player_line_up)

    def get_all_fixtures_ids_to_collect(self) -> List[int]:
        surrounding = self._fixtures_db_manager.get_games_in_surrounding_n_hours(
            hours=0.33, favourite=True
        ) + self._fixtures_db_manager.get_games_in_surrounding_n_hours(
            hours=-0.33, favourite=True
        )

        filtered_fixtures_ids = []

        for fixture in surrounding:
            fixture_line_ups = self._lines_ups_db_manager.get_fixture_line_ups(
                fixture.id
            )
            fixture_utc_date = get_formatted_date(fixture.utc_date)

            if len(fixture_line_ups):
                logger.info(
                    f"Line Ups for fixture {fixture.id} ({fixture.home_team} vs. {fixture.away_team}) were already "
                    f"collected"
                )
                continue
            elif (
                fixture_utc_date > datetime.datetime.utcnow()
                and fixture.line_up_check_attempt == 1
            ):
                logger.info(
                    f"Line Ups for fixture {fixture.id} ({fixture.home_team} vs. {fixture.away_team}) were already attempted to collect before the game."
                )
                continue
            elif fixture.line_up_check_attempt == 2:
                logger.info(
                    f"Line Ups for fixture {fixture.id} ({fixture.home_team} vs. {fixture.away_team}) were already attempted to collect max. times"
                )
                continue

            filtered_fixtures_ids.append(fixture.id)

        return filtered_fixtures_ids
