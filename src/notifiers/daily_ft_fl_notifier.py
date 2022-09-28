import inspect
import os
import sys
from typing import Optional

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
project_dir = os.path.join(parent_dir, "..")
sys.path.insert(0, parent_dir)
sys.path.insert(1, project_dir)

from src.db.fixtures_db_manager import FixturesDBManager
from src.db.notif_sql_models import TimeZone
from src.emojis import Emojis
from src.senders.telegram_sender import send_telegram_message
from src.utils.fixtures_utils import convert_db_fixture

fixtures_db_manager = FixturesDBManager()


def _get_user_main_time_zone(user: str) -> Optional[TimeZone]:
    user_time_zones = fixtures_db_manager.get_user_time_zones(user)
    user_main_time_zone = None
    filtered_user_main_time_zone = [
        time_zone.time_zone for time_zone in user_time_zones if time_zone.is_main_tz
    ]

    if len(filtered_user_main_time_zone):
        user_main_time_zone = fixtures_db_manager.get_time_zone(
            filtered_user_main_time_zone[0]
        )[0]

    return user_main_time_zone


def notify_ft_teams_playing() -> None:
    users = fixtures_db_manager.get_favourite_teams_users()

    for user in users:
        user_fixtures_to_notif = []

        user_main_time_zone = _get_user_main_time_zone(user)

        favourite_teams = [
            team for team in fixtures_db_manager.get_favourite_teams(user)
        ]
        today_matches = fixtures_db_manager.get_games_in_surrounding_n_days(
            0, time_zone=user_main_time_zone.name if user_main_time_zone else ""
        )

        for fixture in today_matches:
            if (
                fixture.away_team in favourite_teams
                or fixture.home_team in favourite_teams
            ):
                converted_fixture = convert_db_fixture(fixture)
                user_fixtures_to_notif.append(converted_fixture)

        if user_fixtures_to_notif:
            notif_text = (
                "One of your favourite teams is "
                if len(user_fixtures_to_notif) == 1
                else "Some of your favourite teams are "
            )
            initial_notif_text = f"Hi! {Emojis.WAVING_HAND.value}\n{notif_text}playing today {Emojis.TELEVISION.value}"

            fixtures_text = "\n\n".join(
                [fixture.one_line_telegram_repr() for fixture in user_fixtures_to_notif]
            )
            final_text = f"{initial_notif_text}\n\n{fixtures_text}"

            send_telegram_message(user, final_text)


def notify_fl_leagues_playing() -> None:
    users = fixtures_db_manager.get_favourite_leagues_users()

    for user in users:
        user_fixtures_to_notif = []

        user_main_time_zone = _get_user_main_time_zone(user)

        favourite_leagues = fixtures_db_manager.get_favourite_leagues(user)

        today_matches = fixtures_db_manager.get_games_in_surrounding_n_days(
            0,
            leagues=favourite_leagues,
            time_zone=user_main_time_zone.name if user_main_time_zone else "",
        )

        for fixture in today_matches:
            converted_fixture = convert_db_fixture(fixture)
            user_fixtures_to_notif.append(converted_fixture)

        if user_fixtures_to_notif:
            initial_notif_text = f"Hi! {Emojis.WAVING_HAND.value}\nThere are matches on your favourite leagues today {Emojis.TELEVISION.value}"

            fixtures_text = "\n\n".join(
                [fixture.one_line_telegram_repr() for fixture in user_fixtures_to_notif]
            )
            final_text = f"{initial_notif_text}\n\n{fixtures_text}"

            send_telegram_message(user, final_text)


if __name__ == "__main__":
    notify_ft_teams_playing()
    notify_fl_leagues_playing()
