import inspect
import os
import sys

import pytz

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
srcdir = os.path.join(parentdir, "..")
project_dir = os.path.join(srcdir, "..")
sys.path.insert(0, parentdir)
sys.path.insert(1, srcdir)
sys.path.insert(2, project_dir)

from src.db.db_manager import NotifierDBManager
from src.db.notif_sql_models import TimeZone

zones = pytz.all_timezones

notifier_db_manager = NotifierDBManager()

db_time_zones = [TimeZone(name=zone) for zone in zones]

notifier_db_manager.insert_records(db_time_zones)
