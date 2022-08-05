import random
from datetime import datetime
from typing import List, Optional, Tuple

from src.db.fixtures_db_manager import FixturesDBManager
from src.db.notif_sql_models import Fixture
from src.db.notif_sql_models import ManagedLeague as DBManagedLeague
from src.db.notif_sql_models import ManagedTeam as DBManagedTeam
from src.db.notif_sql_models import Team as DBTeam
from src.emojis import Emojis
from src.notifier_logger import get_logger
from src.telegram_bot.bot_constants import MESSI_PHOTO
from src.utils.date_utils import get_date_spanish_text_format
from src.utils.fixtures_utils import convert_db_fixture, get_head_to_heads
from src.utils.notification_text_utils import (
    telegram_last_fixture_league_notification,
    telegram_last_fixture_team_notification,
    telegram_next_league_fixture_notification,
    telegram_next_team_fixture_notification,
)

logger = get_logger(__name__)


class NotifierBotCommandsHandler:
    def __init__(self):
        self._fixtures_db_manager: FixturesDBManager = FixturesDBManager()
        self._managed_teams: List[
            DBManagedTeam
        ] = self._fixtures_db_manager.get_managed_teams()

    def get_managed_team(self, command: str) -> DBManagedTeam:
        return next(
            (team for team in self._managed_teams if team.command == command),
            None,
        )

    def search_team(self, team_text: str) -> Optional[DBTeam]:
        return self._fixtures_db_manager.get_teams_by_name(team_text)

    def search_league(self, league_text: str) -> Optional[DBTeam]:
        return self._fixtures_db_manager.get_leagues_by_name(league_text)

    def is_available_team(self, team_id: int) -> bool:
        team = self._fixtures_db_manager.get_team(team_id)

        return True if len(team) else False

    def is_available_league(self, league_id: int) -> bool:
        league = self._fixtures_db_manager.get_league(league_id)
        return True if len(league) else False

    def available_command_team_names(self) -> List[str]:
        return [managed_team.command for managed_team in self._managed_teams]

    def available_leagues(self) -> List[str]:
        return self._fixtures_db_manager.get_all_leagues()

    def available_teams_text(self) -> str:
        return "\n".join(
            [
                f"• {available_team}"
                for available_team in self.available_command_team_names()
            ]
        )

    def available_leagues_text(self) -> str:
        leagues = self.available_leagues()
        leagues_texts = [
            f"<strong>{league.id}</strong> - {league.name} ({league.country})"
            for league in leagues
        ]
        return "\n".join(leagues_texts)

    @staticmethod
    def get_fixtures_text(
        converted_fixtures: List[Fixture], played: bool = False, with_date: bool = False
    ) -> List[str]:
        text_limit = 3500
        fixtures_text = ""
        all_fitting_fixtures = []
        current_fitting_fixtures = []

        for fixture in converted_fixtures:
            fixture_text = fixture.one_line_telegram_repr(played, with_date)

            if len(f"{fixtures_text}\n\n{fixture_text}") > text_limit:
                all_fitting_fixtures.append(current_fitting_fixtures)
                fixtures_text = ""
                current_fitting_fixtures = []
            else:
                fixtures_text += "\n\n" + fixture_text
                current_fitting_fixtures.append(fixture)

        if current_fitting_fixtures:
            all_fitting_fixtures.append(current_fitting_fixtures)

        logger.info(f"All fitting fixtures: {all_fitting_fixtures}")

        return [
            "\n\n".join(
                [
                    fitting_fixture.one_line_telegram_repr(played, with_date)
                    for fitting_fixture in fitting_fixtures
                ]
            )
            for fitting_fixtures in all_fitting_fixtures
        ]


class SurroundingMatchesHandler(NotifierBotCommandsHandler):
    def __init__(self, commands_args: List[str], user: str):
        super().__init__()
        self._command_args = commands_args
        self._user = user

    def today_games(self) -> Tuple[str, str]:
        today_games_fixtures = (
            self._fixtures_db_manager.get_games_in_surrounding_n_days(
                0, self._command_args
            )
        )

        if len(today_games_fixtures):
            converted_games = [
                convert_db_fixture(fixture) for fixture in today_games_fixtures
            ]
            texts = self.get_fixtures_text(converted_games)
            leagues = [fixture.championship for fixture in converted_games]
            photo = random.choice([league.logo for league in leagues])
        else:
            leagues_text = (
                f" para las ligas seleccionadas ({', '.join(self._command_args)}) "
                if len(self._command_args)
                else ""
            )
            texts = [
                (
                    f"{Emojis.WAVING_HAND.value} Hola "
                    f"{self._user}, lamentablemente hoy "
                    f"no hay partidos{leagues_text} :("
                )
            ]
            photo = MESSI_PHOTO

        return (texts, photo)

    def yesterday_games(self) -> Tuple[str, str]:
        played_games_fixtures = (
            self._fixtures_db_manager.get_games_in_surrounding_n_days(
                -1, self._command_args
            )
        )

        if len(played_games_fixtures):
            converted_fixtures = [
                convert_db_fixture(fixture) for fixture in played_games_fixtures
            ]
            texts = self.get_fixtures_text(converted_fixtures, played=True)
            leagues = [fixture.championship for fixture in converted_fixtures]
            photo = random.choice([league.logo for league in leagues])
        else:
            leagues_text = (
                f" para las ligas seleccionadas (" f"{', '.join(self._command_args)}) "
                if len(self._command_args)
                else ""
            )
            texts = [
                (
                    f"{Emojis.WAVING_HAND.value} Hola "
                    f"{self._user}, lamentablemente "
                    f"ayer no se jugaron partidos{leagues_text} :("
                )
            ]
            photo = MESSI_PHOTO

        return (texts, photo)

    def tomorrow_games(self) -> Tuple[str, str]:
        tomorrow_games_fixtures = (
            self._fixtures_db_manager.get_games_in_surrounding_n_days(
                1, self._command_args
            )
        )

        if len(tomorrow_games_fixtures):
            converted_fixtures = [
                convert_db_fixture(fixture) for fixture in tomorrow_games_fixtures
            ]
            texts = self.get_fixtures_text(converted_fixtures)
            leagues = [fixture.championship for fixture in converted_fixtures]
            photo = random.choice([league.logo for league in leagues])
        else:
            leagues_text = (
                f" para las ligas seleccionadas (" f"{', '.join(self._command_args)}) "
                if len(self._command_args)
                else ""
            )
            texts = [
                (
                    f"{Emojis.WAVING_HAND.value} Hola "
                    f"{self._user}, lamentablemente mañana "
                    f"no hay partidos{leagues_text} :("
                )
            ]
            photo = MESSI_PHOTO

        return (texts, photo)


class SearchTeamLeagueCommandHandler(NotifierBotCommandsHandler):
    def __init__(self, commands_args: List[str], user: str):
        super().__init__()
        self._command_args = commands_args
        self._user = user

    def validate_command_input(self) -> str:
        response = ""
        if len(self._command_args) < 1:
            response = "Debés ingresar un texto para la búsqueda"
        else:
            team = " ".join(self._command_args)
            if len(team) < 4:
                response = "El texto de búsqueda debe tener al menos <strong>4</strong> caracteres de longitud."

        return response

    def search_team_notif(self) -> str:
        team = " ".join(self._command_args)

        found_teams = self.search_team(team)

        if found_teams:
            found_teams_texts = [
                f"<strong>{team.id}</strong> - {team.name}" for team in found_teams
            ]
            response = "\n".join(found_teams_texts)
        else:
            response = (
                f"Oops! No hay equipos disponibles con el criterio de busqueda '{team}'"
            )

        return response

    def search_league_notif(self) -> str:
        league = " ".join(self._command_args)

        found_leagues = self.search_league(league)

        if found_leagues:
            found_teams_texts = [
                f"<strong>{league.id}</strong> - {league.name}"
                for league in found_leagues
            ]
            response = "\n".join(found_teams_texts)
        else:
            response = f"Oops! No hay torneos disponibles con el criterio de busqueda '{league}'"

        return response


class NextAndLastMatchCommandHandler(NotifierBotCommandsHandler):
    def __init__(self, commands_args: List[str], user: str):
        super().__init__()
        self._command_args = commands_args
        self._user = user

    def validate_command_input(self) -> str:
        response = ""

        if len(self._command_args) < 1:
            response = "Debés ingresar al menos un equipo"
        elif len(self._command_args) > 1:
            response = "Sólo puedes ingresar un equipo"
        else:
            team = self._command_args[0].lower()
            if not self.is_available_team(team):
                response = (
                    f"Oops! '{team}' no está disponible :(\n\n"
                    f"Los equipos disponibles son:\n\n"
                    f"{self.available_teams_text()}"
                )

        return response

    def next_match_team_notif(self) -> Tuple[str, str]:
        team_id = self._command_args[0]
        team = self._fixtures_db_manager.get_team(team_id)[0]

        next_team_db_fixture = self._fixtures_db_manager.get_next_fixture(
            team_id=team_id
        )

        converted_fixture = None

        if len(next_team_db_fixture):
            converted_fixture = convert_db_fixture(next_team_db_fixture[0])
            converted_fixture.head_to_head = get_head_to_heads(
                converted_fixture.home_team.id, converted_fixture.away_team.id
            )

        return (
            telegram_next_team_fixture_notification(
                converted_fixture, team.name, self._user
            )
            if converted_fixture
            else ("No se encontraron partidos.", None)
        )

    def last_match_team_notif(self) -> Tuple[str, str]:
        team_id = self._command_args[0]
        team = self._fixtures_db_manager.get_team(team_id)[0]

        last_team_db_fixture = self._fixtures_db_manager.get_last_fixture(
            team_id=team_id
        )

        converted_fixture = None

        if len(last_team_db_fixture):
            converted_fixture = convert_db_fixture(last_team_db_fixture[0])

        return (
            telegram_last_fixture_team_notification(
                converted_fixture, team.name, self._user
            )
            if converted_fixture
            else ("No se encontraron partidos.", None)
        )

    def upcoming_matches(self) -> Tuple[str, str]:
        team_id = self._command_args[0]
        team = self._fixtures_db_manager.get_team(team_id)[0]

        upcoming_team_fixtures = self._fixtures_db_manager.get_next_fixture(
            team_id=team_id, number_of_fixtures=5
        )

        if len(upcoming_team_fixtures):
            converted_fixtures = [
                convert_db_fixture(fixture) for fixture in upcoming_team_fixtures
            ]
            introductory_text = (
                f"{Emojis.WAVING_HAND.value} Hola {self._user}, los próximos partidos "
                f"de {team.name} son:"
            )
            texts = self.get_fixtures_text(converted_fixtures, with_date=True)
            texts[0] = f"{introductory_text}\n\n{texts[0]}"
            leagues = [fixture.championship for fixture in converted_fixtures]
            photo = random.choice([league.logo for league in leagues])
        else:
            texts = [
                (
                    f"{Emojis.WAVING_HAND.value} Hola "
                    f"{self._user}, lamentablemente no se encontraron próximos partidos para {team.name} :("
                )
            ]
            photo = MESSI_PHOTO

        return (texts, photo)

    def last_matches(self) -> Tuple[str, str]:
        team_id = self._command_args[0]
        team = self._fixtures_db_manager.get_team(team_id)[0]

        last_team_fixtures = self._fixtures_db_manager.get_last_fixture(
            team_id=team_id, number_of_fixtures=5
        )

        if len(last_team_fixtures):
            converted_fixtures = [
                convert_db_fixture(fixture) for fixture in last_team_fixtures
            ]
            introductory_text = (
                f"{Emojis.WAVING_HAND.value} Hola {self._user}, "
                f"los últimos partidos de {team.name} fueron:"
            )
            texts = self.get_fixtures_text(
                converted_fixtures, played=True, with_date=True
            )
            texts[0] = f"{introductory_text}\n\n{texts[0]}"
            leagues = [fixture.championship for fixture in converted_fixtures]
            photo = random.choice([league.logo for league in leagues])
        else:
            texts = [
                (
                    f"{Emojis.WAVING_HAND.value} Hola "
                    f"{self._user}, lamentablemente no se encontraron últimos partidos para {team.name} :("
                )
            ]
            photo = MESSI_PHOTO

        return (texts, photo)


class NextAndLastMatchLeagueCommandHandler(NotifierBotCommandsHandler):
    def __init__(self, commands_args: List[str], user: str):
        super().__init__()
        self._command_args = commands_args
        self._user = user

    def validate_command_input(self) -> str:
        response = ""

        if len(self._command_args) < 1:
            response = "Debés ingresar al menos un torneo"
        elif len(self._command_args) > 1:
            response = "Sólo puedes ingresar un torneo"
        else:
            league = self._command_args[0]
            if not self.is_available_league(league):
                response = (
                    f"Oops! '{league}' no está disponible :(\n\n"
                    f"Los torneos disponibles son:\n\n"
                    f"{self.available_leagues_text()}"
                )

        return response

    def next_match_league_notif(self) -> Tuple[str, str]:
        league_id = self._command_args[0]
        league = self._fixtures_db_manager.get_league(league_id)[0]

        next_league_db_fixture = self._fixtures_db_manager.get_next_fixture(
            league_id=league.id
        )

        converted_fixture = None

        if next_league_db_fixture:
            converted_fixture = convert_db_fixture(next_league_db_fixture)
            converted_fixture.head_to_head = get_head_to_heads(
                converted_fixture.home_team.id, converted_fixture.away_team.id
            )

        return (
            telegram_next_league_fixture_notification(
                converted_fixture, league.name, self._user
            )
            if converted_fixture
            else ("No se encontraron partidos.", None)
        )

    def last_match_league_notif(self) -> Tuple[str, str]:
        league_id = self._command_args[0]
        league = self._fixtures_db_manager.get_league(league_id)[0]

        next_league_db_fixture = self._fixtures_db_manager.get_last_fixture(
            league_id=league.id
        )

        converted_fixture = None

        if next_league_db_fixture:
            converted_fixture = convert_db_fixture(next_league_db_fixture)

        return (
            telegram_last_fixture_league_notification(
                converted_fixture, league.name, self._user
            )
            if converted_fixture
            else ("No se encontraron partidos.", None)
        )

    def next_matches_league_notif(self) -> str:
        league_id = self._command_args[0]
        league = self._fixtures_db_manager.get_league(league_id)[0]

        next_league_db_fixture = self._fixtures_db_manager.get_next_fixture(
            league_id=league.id
        )[0]

        if next_league_db_fixture:
            next_match_date = next_league_db_fixture.bsas_date[:10]
            next_matches = self._fixtures_db_manager.get_fixtures_by_league(
                league.id, next_match_date
            )

            converted_fixtures = [
                convert_db_fixture(fixture) for fixture in next_matches
            ]

            spanish_format_date = get_date_spanish_text_format(
                converted_fixtures[0].bsas_date
            )

            match_date = (
                "HOY!"
                if converted_fixtures[0].bsas_date.date() == datetime.today().date()
                else f"el {Emojis.SPIRAL_CALENDAR.value}{spanish_format_date}"
            )

            telegram_messages = self.get_fixtures_text(converted_fixtures)

            intro_text = (
                f"{Emojis.WAVING_HAND.value}Hola {self._user}! "
                f"\n\nLos próximos partidos de <strong>{league.name} ({league.country[:3].upper()})</strong> son {match_date}\n\n"
            )

            telegram_messages[0] = f"{intro_text}{telegram_messages[0]}"
        else:
            telegram_messages = ["No se encontraron partidos."]

        return telegram_messages
