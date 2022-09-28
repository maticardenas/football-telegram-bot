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
from src.senders.telegram_sender import send_telegram_message
from src.utils.date_utils import get_formatted_date, is_time_between
from src.utils.fixtures_utils import convert_db_fixture
from src.utils.notifier_utils import is_user_subscribed_to_notif

fixtures_db_manager = FixturesDBManager()


def notify_ft_team_game_approaching() -> None:
    surrounding_fixtures = fixtures_db_manager.get_games_in_surrounding_n_hours(0.5)

    for fixture in surrounding_fixtures:
        fixture_time = get_formatted_date(fixture.utc_date).time()

        utc_now = datetime.utcnow()
        end_time = (utc_now + timedelta(hours=0.5)).time()

        if is_time_between(fixture_time, utc_now.time(), end_time):
            favourite_teams_records = fixtures_db_manager.get_favourite_teams_for_team(
                fixture.home_team
            ) + fixtures_db_manager.get_favourite_teams_for_team(fixture.away_team)

            if len(favourite_teams_records):
                for ft_record in favourite_teams_records:
                    if is_user_subscribed_to_notif(ft_record.chat_id, 3):
                        converted_fixture = convert_db_fixture(
                            fixture,
                            user_time_zones=fixtures_db_manager.get_user_time_zones(
                                ft_record.chat_id
                            ),
                        )
                        initial_notif_text = f"Hi! {Emojis.WAVING_HAND.value}\nYour favourite team is playing soon {Emojis.TELEVISION.value}"
                        notif_text = f"{initial_notif_text}\n\n{converted_fixture.telegram_like_repr()}"
                        send_telegram_message(
                            chat_id=ft_record.chat_id, message=notif_text
                        )


if __name__ == "__main__":
    notify_ft_team_game_approaching()