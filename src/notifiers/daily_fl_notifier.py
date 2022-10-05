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
from src.utils.date_utils import get_time_in_time_zone_str, is_time_between
from src.utils.fixtures_utils import convert_db_fixture
from src.utils.notifier_utils import (
    get_user_main_time_zone,
    is_user_subscribed_to_notif,
)

fixtures_db_manager = FixturesDBManager()

logger = get_logger(__name__)


def notify_fl_leagues_playing() -> None:
    users = fixtures_db_manager.get_favourite_leagues_users()

    for user in users:
        logger.info(f"Favourite Leagues Games notifier for user {user}")

        if not is_user_subscribed_to_notif(user, 2):
            logger.info(
                f"User {user} is not subscribed to notification type 2 - Skipping."
            )
            continue

        user_fixtures_to_notif = []
        user_main_time_zone = get_user_main_time_zone(user)
        now = datetime.utcnow()

        if user_main_time_zone:
            logger.info(f"User main timezone - {user_main_time_zone.name}")
            now = get_time_in_time_zone_str(now, user_main_time_zone.name)

        begin_time = (
            now.replace().replace(hour=7, minute=55, second=0, microsecond=0).time()
        )
        end_time = (
            now.replace().replace(hour=8, minute=5, second=0, microsecond=0).time()
        )

        if not is_time_between(now.time(), begin_time, end_time):
            logger.info(
                f"Current time in time zone {user_main_time_zone.name} ({now.time()}) is not between - {begin_time} and {end_time}"
            )
            continue

        favourite_leagues = fixtures_db_manager.get_favourite_leagues(user)

        today_matches = fixtures_db_manager.get_games_in_surrounding_n_days(
            0,
            leagues=favourite_leagues,
            time_zone=user_main_time_zone.name if user_main_time_zone else "",
        )

        for fixture in today_matches:
            converted_fixture = convert_db_fixture(
                fixture, user_time_zones=fixtures_db_manager.get_user_time_zones(user)
            )
            user_fixtures_to_notif.append(converted_fixture)

        if user_fixtures_to_notif:
            initial_notif_text = f"{Emojis.BELL.value}{Emojis.BELL.value}{Emojis.BELL.value}\n\nHi! {Emojis.WAVING_HAND.value}\nThere are matches on your favourite leagues today {Emojis.TELEVISION.value}"

            fixtures_text = "\n\n".join(
                [fixture.one_line_telegram_repr() for fixture in user_fixtures_to_notif]
            )
            final_text = f"{initial_notif_text}\n\n{fixtures_text}"

            logger.info(f"Notifying FL Games Today to user {user} - text: {final_text}")
            send_telegram_message(user, final_text)


if __name__ == "__main__":
    logger.info("*** RUNNING Favourite Leagues Games Notifier ****")
    notify_fl_leagues_playing()
