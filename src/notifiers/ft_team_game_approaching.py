import inspect
import os
import sys
from datetime import datetime, timedelta

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
project_dir = os.path.join(parent_dir, "..")
sys.path.insert(0, parent_dir)
sys.path.insert(1, project_dir)

from src.db.fixtures_db_manager import FixturesDBManager
from src.emojis import Emojis
from src.notifier_constants import NOT_PLAYED_OR_FINISHED_MATCH_STATUSES
from src.notifier_logger import get_logger
from src.senders.telegram_sender import send_telegram_message
from src.utils.date_utils import get_formatted_date, is_time_between
from src.utils.fixtures_utils import convert_db_fixture
from src.utils.notifier_utils import is_user_subscribed_to_notif

fixtures_db_manager = FixturesDBManager()

logger = get_logger(__name__)


def notify_ft_team_game_approaching() -> None:
    surrounding_fixtures = fixtures_db_manager.get_games_in_surrounding_n_hours(0.5)

    for fixture in surrounding_fixtures:
        logger.info(f"Checking game approaching notification for fixture {fixture.id}")
        fixture_time = get_formatted_date(fixture.utc_date).time()

        utc_now = datetime.utcnow()
        end_time = (utc_now + timedelta(minutes=31)).time()

        if is_time_between(fixture_time, utc_now.time(), end_time):
            favourite_teams_records = fixtures_db_manager.get_favourite_teams_for_team(
                fixture.home_team
            ) + fixtures_db_manager.get_favourite_teams_for_team(fixture.away_team)

            if fixture.approach_notified is True:
                logger.info(f"Fixture {fixture.id} was already notified")
                continue

            if fixture.match_status in NOT_PLAYED_OR_FINISHED_MATCH_STATUSES:
                logger.info(
                    f"Fixture {fixture.id} is not notified because of its status"
                )
                continue

            if len(favourite_teams_records):
                chat_ids_to_notify = list(
                    set([ft.chat_id for ft in favourite_teams_records])
                )
                for chat_id in chat_ids_to_notify:
                    if is_user_subscribed_to_notif(chat_id, 3):
                        converted_fixture = convert_db_fixture(
                            fixture,
                            user_time_zones=fixtures_db_manager.get_user_time_zones(
                                chat_id
                            ),
                        )
                        initial_notif_text = f"{Emojis.BELL.value}{Emojis.BELL.value}{Emojis.BELL.value}\n\nHi! {Emojis.WAVING_HAND.value}\nYour favourite team is playing soon {Emojis.TELEVISION.value}"
                        notif_text = f"{initial_notif_text}\n\n{converted_fixture.telegram_like_repr()}"
                        logger.info(
                            f"Notifying FT Game Approaching to user {chat_id} - text: {notif_text}"
                        )
                        send_telegram_message(chat_id=chat_id, message=notif_text)

            fixture.approach_notified = True
            fixtures_db_manager.insert_or_update_fixture(fixture)


if __name__ == "__main__":
    logger.info("*** RUNNING Favourite Team Game Approaching ****")
    notify_ft_team_game_approaching()
