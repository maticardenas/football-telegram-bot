import inspect
import os
import sys
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
project_dir = os.path.join(parent_dir, "..")
sys.path.insert(0, parent_dir)
sys.path.insert(1, project_dir)

from src.db.fixtures_db_manager import FixturesDBManager
from src.emojis import Emojis
from src.notifier_logger import get_logger
from src.senders.telegram_sender import send_telegram_message
from src.utils.date_utils import get_formatted_date
from src.utils.fixtures_utils import convert_db_fixture
from src.utils.notifier_utils import is_user_subscribed_to_notif

fixtures_db_manager = FixturesDBManager()

logger = get_logger(__name__)


def notify_ft_team_game_played() -> None:
    surrounding_fixtures = fixtures_db_manager.get_games_in_surrounding_n_hours(4)

    for fixture in surrounding_fixtures:
        logger.info(f"Checking notification for fixture {fixture.id}")
        fixture_time = get_formatted_date(fixture.utc_date)
        utc_now = datetime.utcnow()

        if utc_now > fixture_time:
            if "finished" not in fixture.match_status.lower():
                logger.info(f"Fixture is not finished yet")
                continue

            if fixture.played_notified is True:
                logger.info(f"Fixture was already notified")
                continue

            favourite_teams_records = fixtures_db_manager.get_favourite_teams_for_team(
                fixture.home_team
            ) + fixtures_db_manager.get_favourite_teams_for_team(fixture.away_team)

            if len(favourite_teams_records):
                logger.info(
                    f"Notifying fixture {fixture.id} - {fixture.home_team} vs. {fixture.away_team}"
                )
                for ft_record in favourite_teams_records:
                    if is_user_subscribed_to_notif(ft_record.chat_id, 4):
                        converted_fixture = convert_db_fixture(
                            fixture,
                            user_time_zones=fixtures_db_manager.get_user_time_zones(
                                ft_record.chat_id
                            ),
                        )
                        team_name = (
                            converted_fixture.home_team.name
                            if converted_fixture.home_team.id == ft_record.team
                            else converted_fixture.away_team.name
                        )
                        initial_notif_text = f"{Emojis.BELL.value}{Emojis.BELL.value}{Emojis.BELL.value}\n\nHi! {Emojis.WAVING_HAND.value}\nYour favourite team <strong>{team_name}</strong> just played today! {Emojis.TELEVISION.value}"
                        notif_text = f"{initial_notif_text}\n\n{converted_fixture.matched_played_telegram_like_repr()}"
                        send_telegram_message(
                            chat_id=ft_record.chat_id, message=notif_text
                        )
                    else:
                        logger.info(
                            f"User {ft_record.chat_id} is not subscribed to played games notifications."
                        )

            fixture.played_notified = True
            fixtures_db_manager.insert_or_update_fixture(fixture)


if __name__ == "__main__":
    logger.info("*** RUNNING Favourite Team Game Played Notifier ****")
    notify_ft_team_game_played()
