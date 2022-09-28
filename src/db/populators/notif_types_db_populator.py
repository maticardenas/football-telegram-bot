import inspect
import os
import sys

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
srcdir = os.path.join(parentdir, "..")
project_dir = os.path.join(srcdir, "..")
sys.path.insert(0, parentdir)
sys.path.insert(1, srcdir)
sys.path.insert(2, project_dir)

from src.db.db_manager import NotifierDBManager
from src.db.notif_sql_models import NotifType

notification_types = [
    {"name": "FT Today", "description": "Favourite teams matches today."},
    {"name": "FL Today", "description": "Favourite leagues matches today."},
    {"name": "Upcoming FT", "description": "Upcoming favourite team match (<30 min.)."},
    {
        "name": "Played FT",
        "description": "Played favourite team match with result after it finished.",
    },
]


notifier_db_manager = NotifierDBManager()

for notification_type in notification_types:
    notif_type = NotifType(
        name=notification_type["name"], description=notification_type["description"]
    )

    notifier_db_manager.insert_record(notif_type)
