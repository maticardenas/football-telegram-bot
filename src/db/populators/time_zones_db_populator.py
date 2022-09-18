import pytz

from src.db.db_manager import NotifierDBManager
from src.db.notif_sql_models import TimeZone

zones = pytz.all_timezones

notifier_db_manager = NotifierDBManager()

db_time_zones = [TimeZone(name=zone) for zone in zones]

notifier_db_manager.insert_records(db_time_zones)
