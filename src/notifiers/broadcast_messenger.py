import inspect
import os
import sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
project_dir = os.path.join(parent_dir, "..")
sys.path.insert(0, parent_dir)
sys.path.insert(1, project_dir)

from src.db.fixtures_db_manager import FixturesDBManager
from src.notifier_logger import get_logger
from src.notifiers.user_messages import LANGUAGES_ENABLEMENT, STATISTICS_KICK_OFF
from src.senders.telegram_sender import send_telegram_message

logger = get_logger(__name__)

fixtures_db_manager = FixturesDBManager()


def notify_all_users(message: str):
    all_users = (
        fixtures_db_manager.get_favourite_teams_users()
        + fixtures_db_manager.get_favourite_leagues_users()
    )

    all_users_filtered = []

    for user in all_users:
        if user not in all_users_filtered:
            all_users_filtered.append(user)

    for user in all_users_filtered:
        logger.info(f"Sending broadcast message to user {user}")
        send_telegram_message(chat_id=user, message=message)


if __name__ == "__main__":
    notify_all_users(STATISTICS_KICK_OFF)
