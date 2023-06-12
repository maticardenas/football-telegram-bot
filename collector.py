import sys

from src.collectors.lineups_collector import LineUpsCollector
from src.notifier_logger import get_logger

logger = get_logger(__name__)

lu_collector = LineUpsCollector()


collectors = {"line_ups": lu_collector.collect_line_ups}


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        logger.info("MISSING ARGUMENT!")
        sys.exit()

    collectors.get(sys.argv[1])()
