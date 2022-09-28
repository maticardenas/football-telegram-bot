from typing import Optional

from src.db.fixtures_db_manager import FixturesDBManager
from src.db.notif_sql_models import NotifConfig, TimeZone

fixtures_db_manager = FixturesDBManager()


def is_user_subscribed_to_notif(user: str, notif_type: int) -> bool:
    user_config = fixtures_db_manager.get_user_notif_config(user)

    if len(user_config):
        config_for_type: NotifConfig = list(
            filter(lambda config: config.notif_type == notif_type, user_config)
        )[0]
        return config_for_type.status == 1

    return False


def get_user_main_time_zone(user: str) -> Optional[TimeZone]:
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
