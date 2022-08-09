from typing import Any, List

from sqlmodel import Session, SQLModel, create_engine

from config.notif_config import NotifConfig
from src.notifier_logger import get_logger

logger = get_logger(__name__)


class NotifierDBManager:
    ENGINE = None

    def __init__(self) -> None:
        NotifierDBManager.ENGINE = (
            create_engine(
                NotifConfig.POSTGRES_DB_URL,
                connect_args={
                    "user": NotifConfig.DB_USER,
                    "password": NotifConfig.DB_PASS,
                },
                echo=True,
            )
            if not NotifierDBManager.ENGINE
            else NotifierDBManager.ENGINE
        )

        self._engine = NotifierDBManager.ENGINE

    def create_db_and_tables(self) -> None:
        logger.info("Creating database and tables")
        SQLModel.metadata.create_all(self._engine)

    def insert_record(self, db_object: Any) -> None:
        session = Session(self._engine)
        session.add(db_object)
        session.commit()

    def insert_records(self, db_objects: List[Any]) -> None:
        with Session(self._engine) as session:
            for db_object in db_objects:
                session.add(db_object)
                session.commit()

    def delete_record(self, db_object: Any) -> None:
        session = Session(self._engine)
        session.delete(db_object)
        session.commit()

    def select_records(self, statement):
        with Session(self._engine) as session:
            return session.exec(statement).all()
