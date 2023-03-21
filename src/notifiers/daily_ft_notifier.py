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
from src.telegram_bot.bot_commands_handler import NotifierBotCommandsHandler
from src.utils.date_utils import get_time_in_time_zone_str, is_time_between
from src.utils.fixtures_utils import convert_db_fixture
from src.utils.notifier_utils import (
    get_user_main_time_zone,
    get_user_notif_config,
    is_user_subscribed_to_notif,
)

fixtures_db_manager = FixturesDBManager()


logger = get_logger(__name__)

NOTIF_TYPE = 1


def notify_ft_teams_playing() -> None:
    users = fixtures_db_manager.get_favourite_teams_users()

    for user in users:
        logger.info(f"Favourite Team Games notifier for user {user}")

        if not is_user_subscribed_to_notif(user, NOTIF_TYPE):
            logger.info(
                f"User {user} is not subscribed to notification type 1 - Skipping."
            )
            continue

        notif_config = get_user_notif_config(NOTIF_TYPE, user)
        notif_hour = int(notif_config.time.split(":")[0])

        user_fixtures_to_notif = []
        user_main_time_zone = get_user_main_time_zone(user)
        now = datetime.utcnow()

        if user_main_time_zone:
            logger.info(f"User main timezone - {user_main_time_zone.name}")
            now = get_time_in_time_zone_str(now, user_main_time_zone.name)

        begin_time = (
            now.replace()
            .replace(hour=notif_hour - 1, minute=55, second=0, microsecond=0)
            .time()
        )
        end_time = (
            now.replace()
            .replace(hour=notif_hour, minute=5, second=0, microsecond=0)
            .time()
        )

        if not is_time_between(now.time(), begin_time, end_time):
            logger.info(
                f"Current time in time zone {user_main_time_zone.name if user_main_time_zone else 'UTC'} ({now.time()}) is not between - {begin_time} and {end_time}"
            )
            continue

        favourite_teams = [
            team for team in fixtures_db_manager.get_favourite_teams(user)
        ]
        today_matches = fixtures_db_manager.get_surround_games_in_time_zone(
            "today", time_zone=user_main_time_zone.name if user_main_time_zone else ""
        )

        for fixture in today_matches:
            if (
                fixture.away_team in favourite_teams
                or fixture.home_team in favourite_teams
            ):
                converted_fixture = convert_db_fixture(
                    fixture,
                    user_time_zones=fixtures_db_manager.get_user_time_zones(user),
                )
                if converted_fixture.get_time_in_main_zone() > now:
                    user_fixtures_to_notif.append(converted_fixture)

        if user_fixtures_to_notif:
            notif_text = (
                "One of your favourite teams is "
                if len(user_fixtures_to_notif) == 1
                else "Some of your favourite teams are "
            )
            initial_notif_text = f"{Emojis.BELL.value}{Emojis.BELL.value}{Emojis.BELL.value}\n\nHi! {Emojis.WAVING_HAND.value}\n{notif_text}playing today {Emojis.TELEVISION.value}"

            fixtures_text = "\n\n".join(
                [fixture.one_line_telegram_repr() for fixture in user_fixtures_to_notif]
            )
            final_text = f"{initial_notif_text}\n\n{fixtures_text}"

            logger.info(f"Notifying FT Games Today to user {user} - text: {final_text}")
            notifier_commands_handler = NotifierBotCommandsHandler(user)
            user_lang = notifier_commands_handler.get_user_language(user)
            send_telegram_message(chat_id=user, message=final_text, lang=user_lang)


if __name__ == "__main__":
    logger.info("*** RUNNING Favourite Leagues Games Notifier ****")
    notify_ft_teams_playing()
