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

from src.db.fixtures_db_manager import FixturesDBManager
from src.db.db_manager import NotifierDBManager

notifier_db_manager = NotifierDBManager()

fixtures_db_manager = FixturesDBManager()

users = fixtures_db_manager.get_all_notif_users()

for user in users:
    fixtures_db_manager.insert_or_update_user_notif_config(6, user)
