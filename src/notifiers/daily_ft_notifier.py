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
from src.db.notif_sql_models import NotifConfig
from src.emojis import Emojis
from src.notifier_constants import NOT_PLAYED_OR_FINISHED_MATCH_STATUSES
from src.notifier_logger import get_logger
from src.senders.telegram_sender import send_telegram_message
from src.telegram_bot.command_handlers.bot_commands_handler import (
    NotifierBotCommandsHandler,
)
from src.telegram_bot.command_handlers.statistics_command_handler import (
    TeamStatisticsBotCommandsHandler,
)
from src.utils.date_utils import get_time_in_time_zone_str, is_time_between
from src.utils.fixtures_utils import convert_db_fixture
from src.utils.notifier_utils import (
    get_user_main_time_zone,
    get_user_notif_config,
    is_user_subscribed_to_notif,
)

logger = get_logger(__name__)


class DailyFTNotifier:
    def __init__(self, notif_type: int) -> None:
        self._notif_type = notif_type
        self._fixtures_db_manager = FixturesDBManager()

    def notify_daily_ft(self) -> NotifConfig:
        users = self._fixtures_db_manager.get_favourite_teams_users()
        for user in users:
            logger.info(f"Favourite Team Games notifier for user {user}")

            if not is_user_subscribed_to_notif(user, self._notif_type):
                logger.info(
                    f"User {user} is not subscribed to notification type {self._notif_type} - Skipping."
                )
                continue

            notif_config = get_user_notif_config(self._notif_type, user)
            notif_hour = int(notif_config.time.split(":")[0])

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

            # if not is_time_between(now.time(), begin_time, end_time):
            #     logger.info(
            #         f"Current time in time zone {user_main_time_zone.name if user_main_time_zone else 'UTC'} ("
            #         f"{now.time()}) is not between - {begin_time} and {end_time}"
            #     )
            #     continue

            favourite_teams = [
                team for team in self._fixtures_db_manager.get_favourite_teams(user)
            ]

            if self._notif_type == 1:
                self._notify_today_ft(favourite_teams, user, user_main_time_zone, now)
            else:
                self._notify_played_ft_stats(
                    favourite_teams, user, user_main_time_zone, now
                )

    def _notify_today_ft(
        self, favourite_teams: list, user: str, user_main_time_zone, now: datetime
    ):
        user_fixtures_to_notif = []
        today_matches = self._fixtures_db_manager.get_surround_games_in_time_zone(
            "today", time_zone=user_main_time_zone.name if user_main_time_zone else ""
        )

        for fixture in today_matches:
            if (
                fixture.away_team in favourite_teams
                or fixture.home_team in favourite_teams
            ):
                converted_fixture = convert_db_fixture(
                    fixture,
                    user_time_zones=self._fixtures_db_manager.get_user_time_zones(user),
                )
                if converted_fixture.get_time_in_main_zone() > now:
                    user_fixtures_to_notif.append(converted_fixture)

        if user_fixtures_to_notif:
            notif_text = (
                "One of your favourite teams is "
                if len(user_fixtures_to_notif) == 1
                else "Some of your favourite teams are "
            )
            initial_notif_text = (
                f"{Emojis.BELL.value}{Emojis.BELL.value}{Emojis.BELL.value}\n\nHi! "
                f"{Emojis.WAVING_HAND.value}\n{notif_text}playing today {Emojis.TELEVISION.value}"
            )
            fixtures_text = "<not_translate>\n\n</not_translate>".join(
                [fixture.one_line_telegram_repr() for fixture in user_fixtures_to_notif]
            )
            final_text = f"{initial_notif_text}<not_translate>\n\n</not_translate>{fixtures_text}"
            logger.info(f"Notifying FT Games Today to user {user} - text: {final_text}")
            notifier_commands_handler = NotifierBotCommandsHandler(user)
            user_lang = notifier_commands_handler.get_user_language(user)
            send_telegram_message(
                chat_id=user, message=final_text, lang=user_lang.short_name
            )

    def _notify_played_ft_stats(
        self, favourite_teams: list, user: str, user_main_time_zone, now: datetime
    ):
        user_fixtures_to_notif = []
        yesterday_matches = self._fixtures_db_manager.get_surround_games_in_time_zone(
            "yesterday",
            time_zone=user_main_time_zone.name if user_main_time_zone else "",
        )

        notifier_commands_handler = NotifierBotCommandsHandler(user)
        user_lang = notifier_commands_handler.get_user_language(user)

        for fixture in yesterday_matches:
            if (
                fixture.away_team in favourite_teams
                or fixture.home_team in favourite_teams
            ) and not (
                fixture.match_status in NOT_PLAYED_OR_FINISHED_MATCH_STATUSES
                or "half" in fixture.match_status
                or fixture.home_score is None
                or fixture.away_score is None
            ):
                converted_fixture = convert_db_fixture(
                    fixture,
                    user_time_zones=self._fixtures_db_manager.get_user_time_zones(user),
                )
                logger.info(
                    f"Converted fixture {converted_fixture.home_team.name} vs {converted_fixture.away_team.name}"
                )
                if converted_fixture.get_time_in_main_zone() < now:
                    logger.info(
                        f"Appending fixture {converted_fixture.home_team.name} vs {converted_fixture.away_team.name} to be notified."
                    )
                    user_fixtures_to_notif.append(converted_fixture)

        if user_fixtures_to_notif:
            notif_text = (
                "One of your favourite teams  "
                if len(user_fixtures_to_notif) == 1
                else "Some of your favourite teams "
            )
            initial_notif_text = (
                f"{Emojis.BELL.value}{Emojis.BELL.value}{Emojis.BELL.value}\n\nHi! "
                f"{Emojis.WAVING_HAND.value}\n{notif_text}played yesterday "
                f"{Emojis.TELEVISION.value}\n\n"
                f"{Emojis.CHART_INCREASING.value} Here you have an updated summary {Emojis.DOWN_FACING_FIST.value}\n\n"
            )
            send_telegram_message(
                chat_id=user, message=initial_notif_text, lang=user_lang.short_name
            )

        for fixture in user_fixtures_to_notif:
            team_id = (
                fixture.home_team.id
                if fixture.home_team.id in favourite_teams
                else fixture.away_team.id
            )
            stats_notifier_commands_handler = TeamStatisticsBotCommandsHandler(team_id)

            text, photo = stats_notifier_commands_handler.teams_summary()
            logger.info(
                f"Notifying stats for {converted_fixture.home_team.name} vs {converted_fixture.away_team.name}"
            )

            send_telegram_message(
                chat_id=user, message=text, photo=photo, lang=user_lang.short_name
            )


if __name__ == "__main__":
    logger.info("*** RUNNING Favourite Teams Games Notifier ****")
    if len(sys.argv) <= 1:
        logger.info("MISSING ARGUMENT!")

    notif_type = 1 if sys.argv[1] == "ft_today" else 5
    daily_ft_notifier = DailyFTNotifier(notif_type=notif_type)
    daily_ft_notifier.notify_daily_ft()
