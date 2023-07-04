import random
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import asc, desc
from sqlmodel import func, or_, select

from src.db.db_manager import NotifierDBManager
from src.db.notif_sql_models import ConfigLanguage as DBConfigLanguage
from src.db.notif_sql_models import Country as DBCountry
from src.db.notif_sql_models import Event as DBEvent
from src.db.notif_sql_models import FavouriteLeague as DBFavouriteLeague
from src.db.notif_sql_models import FavouriteTeam as DBFavouriteTeam
from src.db.notif_sql_models import Fixture as DBFixture
from src.db.notif_sql_models import Language as DBLanguage
from src.db.notif_sql_models import League as DBLeague
from src.db.notif_sql_models import NotifConfig as DBNotifConfig
from src.db.notif_sql_models import NotifType as DBNotifType
from src.db.notif_sql_models import Player as DBPlayer
from src.db.notif_sql_models import Team as DBTeam
from src.db.notif_sql_models import TimeZone as DBTimeZone
from src.db.notif_sql_models import UserTimeZone as DBUserTimeZone
from src.notifier_constants import SURROUNDING_INDEXES
from src.notifier_logger import get_logger
from src.utils.date_utils import (
    get_date_diff,
    get_formatted_date,
    get_time_in_time_zone,
    get_time_in_time_zone_str,
)
from src.utils.db_utils import remove_duplicate_fixtures

logger = get_logger(__name__)


if TYPE_CHECKING:
    from src.entities import Championship, Event, FixtureForDB, Player, Team


class EventConverter:
    @staticmethod
    def to_db_model(event: "Event") -> DBEvent:
        return DBEvent(
            fixture=event.fixture_id,
            time=event.time.elapsed,
            time_extra=event.time.extra,
            team=event.team.id,
            player=event.player.id,
            assist=event.assist.id,
            type=event.type,
            detail=event.detail,
            comments=event.comments,
        )


class FixturesDBManager:
    def __init__(self):
        self._notifier_db_manager = NotifierDBManager()

    def get_all_fixtures(self) -> List[Optional[DBFixture]]:
        return self._notifier_db_manager.select_records(select(DBFixture))

    def get_all_countries(self) -> List[Optional[DBCountry]]:
        return self._notifier_db_manager.select_records(select(DBCountry))

    def get_countries_by_name(self, name: str) -> Optional[DBTeam]:
        countries_statement = (
            select(DBCountry)
            .where(func.lower(DBCountry.name).ilike(f"%{name.lower()}%"))
            .order_by(asc(DBCountry.id))
        )
        return self._notifier_db_manager.select_records(countries_statement)

    def get_country(self, country_id: int) -> Optional[DBCountry]:
        country_statement = select(DBCountry).where(DBCountry.id == country_id)
        return self._notifier_db_manager.select_records(country_statement)

    def get_team(self, team_id: int) -> Optional[DBTeam]:
        team_statement = select(DBTeam).where(DBTeam.id == team_id)
        return self._notifier_db_manager.select_records(team_statement)

    def get_all_favourite_teams(self) -> List[Optional[DBTeam]]:
        favourite_teams_statement = select(DBFavouriteTeam.team).distinct()

        return self._notifier_db_manager.select_records(favourite_teams_statement)

    def get_all_favourite_leagues(self) -> List[Optional[DBTeam]]:
        favourite_leagues_statement = select(DBFavouriteLeague.league).distinct()

        return self._notifier_db_manager.select_records(favourite_leagues_statement)

    def get_favourite_teams(self, chat_id: str) -> List[Optional[DBTeam]]:
        favourite_teams_statement = select(DBFavouriteTeam.team).where(
            DBFavouriteTeam.chat_id == str(chat_id)
        )

        return self._notifier_db_manager.select_records(favourite_teams_statement)

    def get_favourite_teams_for_team(
        self, team_id: int
    ) -> List[Optional[DBFavouriteTeam]]:
        favourite_teams_statement = select(DBFavouriteTeam).where(
            DBFavouriteTeam.team == team_id
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
        teams_statement = (
            select(DBLeague)
            .where(func.lower(DBLeague.name).ilike(f"%{name.lower()}%"))
            .order_by(asc(DBLeague.name))
        )
        return self._notifier_db_manager.select_records(teams_statement)

    def get_leagues_by_country(self, country_name: str) -> Optional[DBTeam]:
        teams_statement = (
            select(DBLeague)
            .where(func.lower(DBLeague.country).ilike(f"%{country_name.lower()}%"))
            .order_by(asc(DBLeague.id))
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
        teams_statement = (
            select(DBTimeZone)
            .where(func.lower(DBTimeZone.name).ilike(f"%{name.lower()}%"))
            .order_by(asc(DBTimeZone.name))
        )
        return self._notifier_db_manager.select_records(teams_statement)

    def get_teams_by_name(self, name: str) -> Optional[DBTeam]:
        teams_statement = (
            select(DBTeam)
            .where(func.lower(DBTeam.name).ilike(f"%{name.lower()}%"))
            .order_by(asc(DBTeam.name))
        )
        return self._notifier_db_manager.select_records(teams_statement)

    def get_games_in_surrounding_n_days(
        self,
        days: int,
        leagues: List[int] = [],
        teams: List[int] = [],
    ) -> List[Optional[DBFixture]]:
        surrounding_fixtures = []

        if days > 0:
            days_range = range(1, days + 1)
        elif days < 0:
            days_range = range(days, 0)
        else:
            days_range = range(0, 1)

        statement = select(DBFixture)

        for day in days_range:
            utc_today = datetime.utcnow()
            surrounding_day = utc_today + timedelta(days=day)
            games_date = str(surrounding_day.date())
            statement.where(DBFixture.utc_date.ilike(games_date))

        if len(leagues):
            league_statement = statement.where(DBFixture.league.in_(leagues))
            surrounding_fixtures += self._notifier_db_manager.select_records(
                league_statement
            )
        elif len(teams):
            team_statement = statement.where(
                or_(DBFixture.home_team.in_(teams), DBFixture.away_team.in_(teams))
            )
            team_fixtures = self._notifier_db_manager.select_records(team_statement)

            surrounding_fixtures = remove_duplicate_fixtures(team_fixtures)
        else:
            surrounding_fixtures += self._notifier_db_manager.select_records(statement)

        surrounding_fixtures.sort(key=lambda fixture: fixture.utc_date)

        return surrounding_fixtures

    def get_surround_games_in_time_zone(
        self,
        surround_type: str,
        leagues: List[int] = [],
        teams: List[int] = [],
        time_zone: str = "UTC",
        exclude_statuses: List[str] = [],
    ) -> List[Optional[DBFixture]]:
        days_to_grab = SURROUNDING_INDEXES.get(surround_type)

        utc_now = datetime.utcnow()
        now_in_time_zone = get_time_in_time_zone_str(utc_now, time_zone)

        dates_to_check = {
            "today": now_in_time_zone.date(),
            "tomorrow": (now_in_time_zone + timedelta(days=1)).date(),
            "yesterday": (now_in_time_zone - timedelta(days=1)).date(),
        }

        date_to_check_in_time_zone = dates_to_check.get(surround_type)

        logger.info(f"Date to check in time zone -> {date_to_check_in_time_zone}")

        today_games = []

        surrounding_fixtures = (
            self.get_games_in_surrounding_n_days(days_to_grab[0], leagues, teams)
            + self.get_games_in_surrounding_n_days(days_to_grab[1], leagues, teams)
            + self.get_games_in_surrounding_n_days(days_to_grab[2], leagues, teams)
        )

        logger.info(
            f"Fixtures: {', '.join([str(fxt.id) for fxt in surrounding_fixtures])}"
        )

        for fixture in surrounding_fixtures:
            if fixture.match_status not in exclude_statuses:
                fixture_date_in_time_zone = get_time_in_time_zone_str(
                    get_formatted_date(fixture.utc_date), time_zone
                ).date()

                if date_to_check_in_time_zone == fixture_date_in_time_zone:
                    today_games.append(fixture)

        return remove_duplicate_fixtures(today_games)

    def get_games_in_surrounding_n_hours(
        self, hours: int, favourite: bool = False, status: str = ""
    ) -> List[Optional[DBFixture]]:
        time_to_check = datetime.now() + timedelta(hours=hours)
        now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        time_to_check_str = datetime.strftime(time_to_check, "%Y-%m-%dT%H:%M:%S")

        if hours > 0:
            statement = (
                select(DBFixture)
                .where(DBFixture.utc_date < time_to_check_str)
                .where(DBFixture.utc_date > now_str)
            )
        else:
            statement = (
                select(DBFixture)
                .where(DBFixture.utc_date > time_to_check_str)
                .where(DBFixture.utc_date < now_str)
            )

        if status:
            statement = statement.where(
                func.lower(DBFixture.match_status).ilike(f"%{status}%")
            )

        surr_fixtures = self._notifier_db_manager.select_records(statement)

        if favourite:
            favourite_leagues_in_db = self.get_all_favourite_leagues()
            favourite_teams_in_db = self.get_all_favourite_teams()
            surr_fixtures = list(
                filter(
                    lambda fixt: fixt.home_team in favourite_teams_in_db
                    or fixt.away_team in favourite_teams_in_db
                    or fixt.league in favourite_leagues_in_db,
                    surr_fixtures,
                )
            )

        random.shuffle(surr_fixtures)

        return surr_fixtures

    def get_fixture_by_id(self, fixture_id: int) -> List[DBFixture]:
        fixtures_statement = select(DBFixture).where(DBFixture.id == fixture_id)

        return self._notifier_db_manager.select_records(fixtures_statement)

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
        self,
        team_id: int = None,
        league_id: int = None,
        number_of_fixtures: int = 1,
        year: str = None,
    ) -> Optional[List[DBFixture]]:
        today = datetime.strftime(datetime.utcnow(), "%Y-%m-%dT%H:%M:%S")

        statement = select(DBFixture).where(DBFixture.utc_date <= today)

        if team_id:
            statement = statement.where(
                or_(DBFixture.home_team == team_id, DBFixture.away_team == team_id)
            )

        if league_id:
            statement = statement.where(DBFixture.league == league_id)

        if year:
            statement = statement.where(DBFixture.utc_date.contains(year))

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

    def get_player(self, player_id: int) -> Optional[DBTeam]:
        player_statement = select(DBPlayer).where(DBPlayer.id == player_id)
        return self._notifier_db_manager.select_records(player_statement)

    def insert_player(self, player: "Player") -> DBPlayer:
        player_statement = select(DBPlayer).where(DBPlayer.id == player.id)
        retrieved_player = self._notifier_db_manager.select_records(player_statement)

        if not len(retrieved_player):
            logger.info(
                f"Inserting Player {player.name} - it does not exist in "
                f"the database"
            )
            db_player = DBPlayer(
                id=player.id,
                name=player.name,
            )

        else:
            logger.info(
                f"Updating PLayer '{player.name}' - it already exists in "
                f"the database"
            )
            db_player = retrieved_player.pop()
            db_player.name = (
                player.name
                if len(db_player.name.split(" ")[0]) < len(player.name.split(" ")[0])
                else db_player.name
            )

        self._notifier_db_manager.insert_record(db_player)

        return self._notifier_db_manager.select_records(player_statement)[0]

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
                country=fixture_team.country,
            )
        else:
            logger.info(
                f"Updating Team '{fixture_team.name}' - it already exists in "
                f"the database"
            )
            db_team = retrieved_team.pop()
            db_team.id = fixture_team.id
            db_team.name = fixture_team.name
            db_team.picture = (
                fixture_team.picture if fixture_team.picture else db_team.picture
            )
            db_team.aliases = fixture_team.aliases
            db_team.country = (
                fixture_team.country if fixture_team.country else db_team.country
            )

        self._notifier_db_manager.insert_record(db_team)

        return self._notifier_db_manager.select_records(team_statement)[0]

    def insert_or_update_fixture(self, fixture: DBFixture) -> None:
        fixture_statement = select(DBFixture).where(DBFixture.id == fixture.id)

        retrieved_fixture = self._notifier_db_manager.select_records(fixture_statement)

        if not len(retrieved_fixture):
            logger.info(
                f"Inserting Fixture {fixture.id} - it does not exist in "
                f"the database"
            )
            db_fixture = fixture
        else:
            logger.info(
                f"Updating Fixture {fixture.id} - it already exists in " f"the database"
            )
            db_fixture: DBFixture = retrieved_fixture.pop()
            db_fixture.id = fixture.id
            db_fixture.utc_date = fixture.utc_date
            db_fixture.bsas_date = fixture.bsas_date
            db_fixture.league = fixture.league
            db_fixture.round = fixture.round
            db_fixture.match_status = fixture.match_status
            db_fixture.referee = fixture.referee
            db_fixture.home_team = fixture.home_team
            db_fixture.away_team = fixture.away_team
            db_fixture.home_score = fixture.home_score
            db_fixture.away_score = fixture.away_score
            db_fixture.penalty_home_score = fixture.penalty_home_score
            db_fixture.penalty_away_score = fixture.penalty_away_score
            db_fixture.venue = fixture.venue
            db_fixture.played_notified = fixture.played_notified
            db_fixture.approach_notified = fixture.approach_notified
            db_fixture.line_up_check_attempt = fixture.line_up_check_attempt

        self._notifier_db_manager.insert_record(db_fixture)

    def save_fixture_event(self, event: "Event") -> None:
        if event.player.name is not None and event.player.id is not None:
            self.insert_player(event.player)
        if event.assist.name is not None and event.assist.id is not None:
            self.insert_player(event.assist)
        logger.info(
            f"Inserting Event {event.type} - {event.player.name} - assist: {event.assist.name}"
        )
        db_event = EventConverter.to_db_model(event)
        self._notifier_db_manager.insert_record(db_event)

    def get_fixture_events(self, fixture_id: int) -> Optional[DBEvent]:
        event_statement = (
            select(DBEvent)
            .where(DBEvent.fixture == fixture_id)
            .order_by(asc(DBEvent.time), asc(DBEvent.time_extra))
        )
        return self._notifier_db_manager.select_records(event_statement)

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
                    penalty_home_score=conv_fix.match_score.penalty_home_score,
                    penalty_away_score=conv_fix.match_score.penalty_away_score,
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
                db_fixture.penalty_home_score = conv_fix.match_score.penalty_home_score
                db_fixture.penalty_away_score = conv_fix.match_score.penalty_away_score
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

    def get_favourite_teams_users(self) -> List[str]:
        statement = select(DBFavouriteTeam.chat_id).distinct()

        return self._notifier_db_manager.select_records(statement)

    def get_favourite_leagues_users(self) -> List[str]:
        statement = select(DBFavouriteLeague.chat_id).distinct()

        return self._notifier_db_manager.select_records(statement)

    def get_all_notif_users(self) -> List[DBNotifConfig]:
        statement = select(DBNotifConfig.chat_id).distinct()

        return self._notifier_db_manager.select_records(statement)

    def get_user_notif_config(self, chat_id: str) -> List[DBNotifConfig]:
        statement = select(DBNotifConfig).where(DBNotifConfig.chat_id == chat_id)

        return self._notifier_db_manager.select_records(statement)

    def insert_or_update_user_notif_config(
        self, notif_type: int, chat_id: str, status: bool = True, time: str = "8:00"
    ) -> None:
        user_notif_config_statement = select(DBNotifConfig).where(
            DBNotifConfig.chat_id == chat_id, DBNotifConfig.notif_type == notif_type
        )

        retrieved_user_notif_config = self._notifier_db_manager.select_records(
            user_notif_config_statement
        )

        if not len(retrieved_user_notif_config):
            logger.info(
                f"Inserting User Notif Config '{chat_id}' - {notif_type} - it does not exist in "
                f"the database"
            )
            db_notif_config = DBNotifConfig(
                chat_id=chat_id,
                notif_type=notif_type,
                status=status,
                time=time,
            )
        else:
            logger.info(
                f"Updating User Notif Config '{chat_id}' - {notif_type} - it already exists in "
                f"the database"
            )
            db_notif_config = retrieved_user_notif_config.pop()
            db_notif_config.chat_id = chat_id
            db_notif_config.notif_type = notif_type
            db_notif_config.status = status
            db_notif_config.time = time

        self._notifier_db_manager.insert_record(db_notif_config)

    def get_notif_type(self, notif_type_id: int) -> List[DBNotifType]:
        statement = select(DBNotifType).where(DBNotifType.id == notif_type_id)

        return self._notifier_db_manager.select_records(statement)

    def get_all_notif_types(self) -> List[DBNotifType]:
        statement = select(DBNotifType).order_by(asc(DBNotifType.id))

        return self._notifier_db_manager.select_records(statement)

    def get_languages_by_name(self, name: str) -> List[Optional[DBLanguage]]:
        languages_statement = (
            select(DBLanguage)
            .where(func.lower(DBLanguage.name).ilike(f"%{name.lower()}%"))
            .order_by(asc(DBLanguage.name))
        )
        return self._notifier_db_manager.select_records(languages_statement)

    def get_language_by_id(self, lang_id: int) -> Optional[DBLanguage]:
        languages_statement = select(DBLanguage).where(DBLanguage.lang_id == lang_id)
        return self._notifier_db_manager.select_records(languages_statement)

    def get_config_language(self, chat_id: str) -> Optional[DBConfigLanguage]:
        languages_statement = select(DBConfigLanguage).where(
            DBConfigLanguage.chat_id == chat_id
        )

        return self._notifier_db_manager.select_records(languages_statement)

    def insert_or_update_user_config_language(self, lang_id: int, chat_id: str) -> None:
        user_config_lang_statement = select(DBConfigLanguage).where(
            DBConfigLanguage.chat_id == chat_id
        )

        retrieved_user_config_lang = self._notifier_db_manager.select_records(
            user_config_lang_statement
        )

        if not len(retrieved_user_config_lang):
            logger.info(
                f"Inserting User Config Language '{chat_id}' - {lang_id} - it does not exist in "
                f"the database"
            )
            db_config_lang = DBConfigLanguage(
                chat_id=chat_id,
                lang_id=lang_id,
            )
        else:
            logger.info(
                f"Updating User Config Language'{chat_id}' - {lang_id} - it already exists in "
                f"the database"
            )
            db_config_lang: DBConfigLanguage = retrieved_user_config_lang.pop()
            db_config_lang.chat_id = chat_id
            db_config_lang.lang_id = lang_id

        self._notifier_db_manager.insert_record(db_config_lang)
