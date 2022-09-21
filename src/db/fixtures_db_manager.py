import random
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import asc, desc
from sqlmodel import func, or_, select

from src.db.db_manager import NotifierDBManager
from src.db.notif_sql_models import FavouriteLeague as DBFavouriteLeague
from src.db.notif_sql_models import FavouriteTeam as DBFavouriteTeam
from src.db.notif_sql_models import Fixture as DBFixture
from src.db.notif_sql_models import League as DBLeague
from src.db.notif_sql_models import Team as DBTeam
from src.db.notif_sql_models import TimeZone as DBTimeZone
from src.db.notif_sql_models import UserTimeZone as DBUserTimeZone
from src.notifier_logger import get_logger
from src.utils.date_utils import (
    get_formatted_date,
    get_time_in_time_zone,
    get_time_in_time_zone_str,
    is_time_in_surrounding_hours,
)
from src.utils.db_utils import remove_duplicate_fixtures

logger = get_logger(__name__)


if TYPE_CHECKING:
    from src.entities import Championship, FixtureForDB, Team


class FixturesDBManager:
    def __init__(self):
        self._notifier_db_manager = NotifierDBManager()

    def get_all_fixtures(self) -> List[Optional[DBFixture]]:
        return self._notifier_db_manager.select_records(select(DBFixture))

    def get_team(self, team_id: int) -> Optional[DBTeam]:
        team_statement = select(DBTeam).where(DBTeam.id == team_id)
        return self._notifier_db_manager.select_records(team_statement)

    def get_favourite_teams(self, chat_id: str) -> List[Optional[DBTeam]]:
        favourite_teams_statement = select(DBFavouriteTeam.team).where(
            DBFavouriteTeam.chat_id == str(chat_id)
        )

        return self._notifier_db_manager.select_records(favourite_teams_statement)

    def get_favourite_leagues(self, chat_id: str) -> List[Optional[DBTeam]]:
        favourite_leagues_statement = select(DBFavouriteLeague.league).where(
            DBFavouriteLeague.chat_id == str(chat_id)
        )

        return self._notifier_db_manager.select_records(favourite_leagues_statement)

    def get_all_favourite_leagues(self) -> List[Optional[DBTeam]]:
        favourite_leagues_statement = select(DBFavouriteLeague.league).distinct()

        return self._notifier_db_manager.select_records(favourite_leagues_statement)

    def get_all_leagues(self, daily_update: bool = False) -> Optional[List[DBLeague]]:
        statement = select(DBLeague)

        if daily_update:
            statement = statement.where(DBLeague.daily_season_fixt_update == "Y")

        statement = statement.order_by(DBLeague.id)

        return self._notifier_db_manager.select_records(statement)

    def get_league(self, league_id: int) -> Optional[DBLeague]:
        league_statement = select(DBLeague).where(DBLeague.id == league_id)
        return self._notifier_db_manager.select_records(league_statement)

    def get_leagues_by_name(self, name: str) -> Optional[DBTeam]:
        teams_statement = select(DBLeague).where(
            func.lower(DBLeague.name).ilike(f"%{name.lower()}%")
        )
        return self._notifier_db_manager.select_records(teams_statement)

    def get_leagues_by_country(self, country_name: str) -> Optional[DBTeam]:
        teams_statement = select(DBLeague).where(
            func.lower(DBLeague.country).ilike(f"%{country_name.lower()}%")
        )
        return self._notifier_db_manager.select_records(teams_statement)

    def get_time_zone(self, time_zone_id: int) -> Optional[DBTimeZone]:
        time_zone_statement = select(DBTimeZone).where(DBTimeZone.id == time_zone_id)
        return self._notifier_db_manager.select_records(time_zone_statement)

    def get_user_time_zones(self, chat_id: str) -> List[Optional[DBUserTimeZone]]:
        user_time_zones_statement = select(DBUserTimeZone).where(
            DBUserTimeZone.chat_id == str(chat_id)
        )

        return self._notifier_db_manager.select_records(user_time_zones_statement)

    def get_time_zones_by_name(self, name: str) -> Optional[DBTimeZone]:
        teams_statement = select(DBTimeZone).where(
            func.lower(DBTimeZone.name).ilike(f"%{name.lower()}%")
        )
        return self._notifier_db_manager.select_records(teams_statement)

    def get_teams_by_name(self, name: str) -> Optional[DBTeam]:
        teams_statement = select(DBTeam).where(
            func.lower(DBTeam.name).ilike(f"%{name.lower()}%")
        )
        return self._notifier_db_manager.select_records(teams_statement)

    def get_games_in_surrounding_n_days(
        self,
        days: int,
        leagues: List[int] = [],
        teams: List[int] = [],
        time_zone: str = "",
    ) -> List[Optional[DBFixture]]:
        surrounding_fixtures = []

        if days > 0:
            days_range = range(1, days + 1)
        elif days < 0:
            days_range = range(days, 0)
        else:
            days_range = range(0, 1)

        for day in days_range:
            utc_today = datetime.utcnow()
            surrounding_day = utc_today + timedelta(days=day)
            games_date = str(surrounding_day.date())

            statement = select(DBFixture).where(DBFixture.utc_date.contains(games_date))

            if len(leagues):
                for league in leagues:
                    league_statement = statement.where(DBFixture.league == league)
                    surrounding_fixtures += self._notifier_db_manager.select_records(
                        league_statement
                    )
            elif len(teams):
                fixtures = []
                for team in teams:
                    team_statement = statement.where(
                        or_(DBFixture.home_team == team, DBFixture.away_team == team)
                    )
                    fixtures += self._notifier_db_manager.select_records(team_statement)

                surrounding_fixtures = remove_duplicate_fixtures(fixtures)
            else:
                surrounding_fixtures += self._notifier_db_manager.select_records(
                    statement
                )

        surrounding_fixtures.sort(key=lambda fixture: fixture.utc_date)

        if time_zone:
            filtered_fixtures = []
            for fixture in surrounding_fixtures:
                fixture_date_time = get_formatted_date(fixture.utc_date)
                time_zone_date_time = get_time_in_time_zone_str(
                    fixture_date_time, time_zone
                )

                if fixture_date_time.date() == time_zone_date_time.date():
                    filtered_fixtures.append(fixture)

            surrounding_fixtures = filtered_fixtures

        return surrounding_fixtures

    def get_games_in_surrounding_n_hours(
        self, hours: int, favourite: bool = False
    ) -> List[Optional[DBFixture]]:
        surrounding_fixtures = []

        today_fixtures = self.get_games_in_surrounding_n_days(0)

        if favourite:
            favourite_leagues_in_db = self.get_all_favourite_leagues()
            today_fixtures = filter(
                lambda fixt: fixt.league in favourite_leagues_in_db, today_fixtures
            )

        for fixture in today_fixtures:
            utc_date = get_formatted_date(fixture.utc_date)

            if is_time_in_surrounding_hours(utc_date.time(), hours):
                surrounding_fixtures.append(fixture)

        random.shuffle(surrounding_fixtures)

        return surrounding_fixtures

    def get_fixtures_by_team(self, team_id: int) -> Optional[List[DBFixture]]:
        fixtures_statement = (
            select(DBFixture)
            .where(
                or_(
                    DBFixture.home_team == team_id,
                    DBFixture.away_team == team_id,
                )
            )
            .order_by(asc(DBFixture.utc_date))
        )

        return self._notifier_db_manager.select_records(fixtures_statement)

    def get_fixtures_by_league(
        self, league_id: int, date: str = ""
    ) -> Optional[List[DBFixture]]:
        fixtures_statement = select(DBFixture).where(DBFixture.league == league_id)

        if date:
            fixtures_statement = fixtures_statement.where(
                DBFixture.utc_date.contains(date)
            )

        fixtures_statement = fixtures_statement.order_by(asc(DBFixture.utc_date))

        return self._notifier_db_manager.select_records(fixtures_statement)

    def get_next_fixture(
        self, team_id: int = None, league_id: int = None, number_of_fixtures: int = 1
    ) -> Optional[List[DBFixture]]:
        today = datetime.strftime(datetime.utcnow(), "%Y-%m-%dT%H:%M:%S")

        statement = select(DBFixture).where(DBFixture.utc_date >= today)

        if team_id:
            statement = statement.where(
                or_(DBFixture.home_team == team_id, DBFixture.away_team == team_id)
            )

        if league_id:
            statement = statement.where(DBFixture.league == league_id)

        statement = statement.order_by(asc(DBFixture.utc_date))

        next_fixtures = self._notifier_db_manager.select_records(statement)

        return (
            next_fixtures[:number_of_fixtures] if len(next_fixtures) else next_fixtures
        )

    def get_last_fixture(
        self, team_id: int = None, league_id: int = None, number_of_fixtures: int = 1
    ) -> Optional[List[DBFixture]]:
        today = datetime.strftime(datetime.utcnow(), "%Y-%m-%dT%H:%M:%S")

        statement = select(DBFixture).where(DBFixture.utc_date <= today)

        if team_id:
            statement = statement.where(
                or_(DBFixture.home_team == team_id, DBFixture.away_team == team_id)
            )

        if league_id:
            statement = statement.where(DBFixture.league == league_id)

        statement = statement.order_by(desc(DBFixture.utc_date))

        next_fixtures = self._notifier_db_manager.select_records(statement)

        return (
            next_fixtures[:number_of_fixtures] if len(next_fixtures) else next_fixtures
        )

    def get_head_to_head_fixtures(self, team_1: str, team_2: str):
        statement = (
            select(DBFixture)
            .where(
                or_(DBFixture.home_team == team_1, DBFixture.away_team == team_1),
            )
            .where(or_(DBFixture.home_team == team_2, DBFixture.away_team == team_2))
            .order_by(DBFixture.utc_date)
        )

        fixtures = self._notifier_db_manager.select_records(statement)

        return [fixture for fixture in fixtures if fixture.home_score is not None]

    def insert_league(self, fixture_league: "Championship") -> DBLeague:
        league_statement = select(DBLeague).where(
            DBLeague.id == fixture_league.league_id
        )
        retrieved_league = self._notifier_db_manager.select_records(league_statement)

        if not len(retrieved_league):
            logger.info(
                f"Inserting League {fixture_league.name} - it does not exist "
                f"in the database"
            )
            db_league = DBLeague(
                id=fixture_league.league_id,
                name=fixture_league.name,
                logo=fixture_league.logo,
                country=fixture_league.country,
            )
        else:
            logger.info(
                f"Updating League '{fixture_league.name}' - it already "
                f"exists in "
                f"the database"
            )
            db_league = retrieved_league.pop()
            db_league.id = fixture_league.league_id
            db_league.name = fixture_league.name
            db_league.logo = fixture_league.logo
            db_league.country = fixture_league.country

        self._notifier_db_manager.insert_record(db_league)

        # object needs to be queried again, as when we insert db_league we
        # are closing the session and then it's out of scope
        # for later using it again
        return self._notifier_db_manager.select_records(league_statement)[0]

    def insert_favourite_team(self, team_id: int, chat_id: str) -> DBFavouriteTeam:
        team = self.get_team(team_id)

        if not len(team):
            raise Exception(f"Team {team_id} doesn't exist.")

        favourite_team_statement = select(DBFavouriteTeam).where(
            DBFavouriteTeam.team == team_id, DBFavouriteTeam.chat_id == chat_id
        )

        retrieved_favourite_team = self._notifier_db_manager.select_records(
            favourite_team_statement
        )

        if not len(retrieved_favourite_team):
            logger.info(
                f"Inserting Favourite Team {team_id} for chat {chat_id}- it does not exist in "
                f"the database"
            )
            db_favourite_team = DBFavouriteTeam(
                team=team_id,
                chat_id=chat_id,
            )

            self._notifier_db_manager.insert_record(db_favourite_team)
        else:
            raise Exception(f"You already have this team as favourite.")

        return self._notifier_db_manager.select_records(favourite_team_statement)[0]

    def insert_favourite_league(self, league_id: int, chat_id: str) -> DBFavouriteTeam:
        league = self.get_league(league_id)

        if not len(league):
            raise Exception(f"League {league_id} doesn't exist.")

        favourite_league_statement = select(DBFavouriteLeague).where(
            DBFavouriteLeague.league == league_id, DBFavouriteLeague.chat_id == chat_id
        )

        retrieved_favourite_league = self._notifier_db_manager.select_records(
            favourite_league_statement
        )

        if not len(retrieved_favourite_league):
            logger.info(
                f"Inserting Favourite League {league_id} for chat {chat_id}- it does not exist in "
                f"the database"
            )
            db_favourite_league = DBFavouriteLeague(
                league=league_id,
                chat_id=chat_id,
            )

            self._notifier_db_manager.insert_record(db_favourite_league)
        else:
            raise Exception(f"You already have this league as favourite.")

        return self._notifier_db_manager.select_records(favourite_league_statement)[0]

    def insert_favourite_team(self, team_id: int, chat_id: str) -> DBFavouriteTeam:
        team = self.get_team(team_id)

        if not len(team):
            raise Exception(f"Team {team_id} doesn't exist.")

        favourite_team_statement = select(DBFavouriteTeam).where(
            DBFavouriteTeam.team == team_id, DBFavouriteTeam.chat_id == chat_id
        )

        retrieved_favourite_team = self._notifier_db_manager.select_records(
            favourite_team_statement
        )

        if not len(retrieved_favourite_team):
            logger.info(
                f"Inserting Favourite Team {team_id} for chat {chat_id}- it does not exist in "
                f"the database"
            )
            db_favourite_team = DBFavouriteTeam(
                team=team_id,
                chat_id=chat_id,
            )

            self._notifier_db_manager.insert_record(db_favourite_team)
        else:
            raise Exception(f"You already have this team as favourite.")

        return self._notifier_db_manager.select_records(favourite_team_statement)[0]

    def insert_user_time_zone(
        self, time_zone_id: int, chat_id: str, main: bool = False
    ) -> DBUserTimeZone:
        time_zone = self.get_time_zone(time_zone_id)

        if not len(time_zone):
            raise Exception(f"Time zone {time_zone} doesn't exist.")

        user_time_zone_statement = select(DBUserTimeZone).where(
            DBUserTimeZone.time_zone == time_zone_id, DBUserTimeZone.chat_id == chat_id
        )

        retrieved_user_time_zone = self._notifier_db_manager.select_records(
            user_time_zone_statement
        )

        if len(retrieved_user_time_zone):
            if retrieved_user_time_zone[0].is_main_tz == main or (
                retrieved_user_time_zone[0].is_main_tz == True and main == False
            ):
                raise Exception(f"You already have configured this time zone.")

        if main:
            main_user_time_zones_statement = select(DBUserTimeZone).where(
                DBUserTimeZone.chat_id == chat_id, DBUserTimeZone.is_main_tz == True
            )

            user_main_time_zone = self._notifier_db_manager.select_records(
                main_user_time_zones_statement
            )

            if len(user_main_time_zone):
                logger.info(
                    f"Deleting previously existing main User Time Zone '{user_main_time_zone[0].time_zone}' for chat "
                    f"{chat_id}"
                )
                self._notifier_db_manager.delete_record(user_main_time_zone[0])

            if len(retrieved_user_time_zone):
                logger.info(
                    f"Deleting previously existing main User Time Zone '{retrieved_user_time_zone[0].time_zone}' for chat "
                    f"{chat_id}"
                )
                self._notifier_db_manager.delete_record(retrieved_user_time_zone[0])

        logger.info(f"Inserting User Time Zone {time_zone_id} for chat {chat_id}")
        db_user_time_zone = DBUserTimeZone(
            time_zone=time_zone_id, chat_id=chat_id, is_main_tz=main
        )

        self._notifier_db_manager.insert_record(db_user_time_zone)

        return self._notifier_db_manager.select_records(user_time_zone_statement)[0]

    def insert_team(self, fixture_team: "Team") -> DBTeam:
        team_statement = select(DBTeam).where(DBTeam.id == fixture_team.id)
        retrieved_team = self._notifier_db_manager.select_records(team_statement)

        if not len(retrieved_team):
            logger.info(
                f"Inserting Team {fixture_team.name} - it does not exist in "
                f"the database"
            )
            db_team = DBTeam(
                id=fixture_team.id,
                name=fixture_team.name,
                picture=fixture_team.picture,
                aliases=fixture_team.aliases,
            )

        else:
            logger.info(
                f"Updating Team '{fixture_team.name}' - it already exists in "
                f"the database"
            )
            db_team = retrieved_team.pop()
            db_team.id = fixture_team.id
            db_team.name = fixture_team.name
            db_team.picture = fixture_team.picture
            db_team.aliases = fixture_team.aliases

        self._notifier_db_manager.insert_record(db_team)

        return self._notifier_db_manager.select_records(team_statement)[0]

    def save_fixtures(self, team_fixtures: List["FixtureForDB"]) -> None:
        db_fixtures = []

        for conv_fix in team_fixtures:
            retrieved_league = self.insert_league(conv_fix.championship)
            retrieved_home_team = self.insert_team(conv_fix.home_team)
            retrieved_away_team = self.insert_team(conv_fix.away_team)

            fixture_statement = select(DBFixture).where(DBFixture.id == conv_fix.id)
            retrieved_fixture = self._notifier_db_manager.select_records(
                fixture_statement
            )

            if not len(retrieved_fixture):
                logger.info(
                    f"Inserting Fixture {conv_fix.home_team.name} vs "
                    f"{conv_fix.away_team.name} - it does not exist in the "
                    f"database"
                )
                db_fixture = DBFixture(
                    id=conv_fix.id,
                    utc_date=conv_fix.utc_date,
                    bsas_date=conv_fix.bsas_date,
                    league=retrieved_league.id,
                    round=conv_fix.round,
                    home_team=retrieved_home_team.id,
                    away_team=retrieved_away_team.id,
                    match_status=conv_fix.match_status,
                    referee=conv_fix.referee,
                    home_score=conv_fix.match_score.home_score,
                    away_score=conv_fix.match_score.away_score,
                    venue=conv_fix.venue,
                )
            else:
                logger.info(
                    f"Updating Fixture {conv_fix.home_team.name} vs "
                    f"{conv_fix.away_team.name}"
                )
                db_fixture = retrieved_fixture.pop()
                db_fixture.id = conv_fix.id
                db_fixture.utc_date = conv_fix.utc_date
                db_fixture.bsas_date = conv_fix.bsas_date
                db_fixture.league = retrieved_league.id
                db_fixture.round = conv_fix.round
                db_fixture.match_status = conv_fix.match_status
                db_fixture.referee = conv_fix.referee
                db_fixture.home_team = retrieved_home_team.id
                db_fixture.away_team = retrieved_away_team.id
                db_fixture.home_score = conv_fix.match_score.home_score
                db_fixture.away_score = conv_fix.match_score.away_score
                db_fixture.venue = conv_fix.venue

            db_fixtures.append(db_fixture)

        self._notifier_db_manager.insert_records(db_fixtures)

    def delete_user_time_zone(self, time_zone_id: int, chat_id: str) -> None:
        time_zone_statement = select(DBUserTimeZone).where(
            DBUserTimeZone.chat_id == chat_id, DBUserTimeZone.time_zone == time_zone_id
        )

        user_time_zone = self._notifier_db_manager.select_records(time_zone_statement)

        if not len(user_time_zone):
            raise Exception(f"You don't have that time zone configured.")

        logger.info(
            f"Removing User Time Zone '{user_time_zone[0].time_zone}' for chat {chat_id}"
        )

        self._notifier_db_manager.delete_record(user_time_zone[0])

    def delete_favourite_team(self, team_id: int, chat_id: str) -> None:
        favourite_team_statement = select(DBFavouriteTeam).where(
            DBFavouriteTeam.chat_id == chat_id, DBFavouriteTeam.team == team_id
        )

        favourite_team = self._notifier_db_manager.select_records(
            favourite_team_statement
        )

        if not len(favourite_team):
            raise Exception(f"You don't have that team added as a favourite.")

        logger.info(f"Removing Favourite Team {team_id} for chat {chat_id}")

        self._notifier_db_manager.delete_record(favourite_team[0])

    def delete_favourite_league(self, league_id: int, chat_id: str) -> None:
        favourite_league_statement = select(DBFavouriteLeague).where(
            DBFavouriteLeague.chat_id == chat_id, DBFavouriteLeague.league == league_id
        )

        favourite_league = self._notifier_db_manager.select_records(
            favourite_league_statement
        )

        if not len(favourite_league):
            raise Exception(f"You don't have that league added as a favourite.")

        logger.info(f"Removing Favourite League {league_id} for chat {chat_id}")

        self._notifier_db_manager.delete_record(favourite_league[0])
