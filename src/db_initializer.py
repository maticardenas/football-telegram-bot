from src.db.db_manager import NotifierDBManager
from src.db.notif_sql_models import *
from src.notifier_logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Initializing database...")
    notifier_db_manager = NotifierDBManager()
    notifier_db_manager.create_db_and_tables()
