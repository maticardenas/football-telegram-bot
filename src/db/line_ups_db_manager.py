from typing import Optional

from sqlalchemy import asc
from sqlmodel import select

from src.db.db_manager import NotifierDBManager
from src.db.notif_sql_models import LineUp as DBLineUp
from src.notifier_logger import get_logger

logger = get_logger(__name__)


class LineUpsDBManager:
    def __init__(self) -> None:
        self._notifier_db_manager = NotifierDBManager()

    def get_fixture_line_ups(self, fixture_id: int) -> Optional[DBLineUp]:
        line_up_statement = select(DBLineUp).where(DBLineUp.fixture == fixture_id)
        return self._notifier_db_manager.select_records(line_up_statement)

    def insert_line_up(self, line_up: DBLineUp) -> DBLineUp:
        line_up_statement = select(DBLineUp).where(
            DBLineUp.fixture == line_up.fixture,
            DBLineUp.player == line_up.player,
            DBLineUp.team == line_up.team,
        )
        retrieved_line_up = self._notifier_db_manager.select_records(line_up_statement)

        if not len(retrieved_line_up):
            logger.info(
                f"Inserting Line Up for fixture {line_up.fixture}, team {line_up.team} and player {line_up.player} - it does not exist in "
                f"the database"
            )
            db_line_up = DBLineUp(
                fixture=line_up.fixture,
                player=line_up.player,
                number=line_up.number,
                team=line_up.team,
                pos=line_up.pos,
                grid=line_up.grid,
            )
        else:
            logger.info(
                f"Updating Line Up for fixture {line_up.fixture}, team {line_up.team} and player {line_up.player} - it already exists in "
                f"the database"
            )
            db_line_up: DBLineUp = retrieved_line_up.pop()
            db_line_up.fixture = line_up.fixture
            db_line_up.player = line_up.player
            db_line_up.number = line_up.number
            db_line_up.pos = line_up.pos
            db_line_up.team = line_up.team
            db_line_up.grid = line_up.grid

        self._notifier_db_manager.insert_record(db_line_up)

        return self._notifier_db_manager.select_records(line_up_statement)[0]
