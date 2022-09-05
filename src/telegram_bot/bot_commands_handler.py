import random
from datetime import datetime
from typing import Any, List, Optional, Tuple

from src.db.fixtures_db_manager import FixturesDBManager
from src.db.notif_sql_models import Fixture
from src.db.notif_sql_models import Team as DBTeam
from src.emojis import Emojis
from src.notifier_logger import get_logger
from src.telegram_bot.bot_constants import MESSI_PHOTO
from src.utils.db_utils import remove_duplicate_fixtures
from src.utils.fixtures_utils import convert_db_fixture, get_head_to_heads
from src.utils.notification_text_utils import (
    telegram_last_team_or_league_fixture_notification,
    telegram_next_team_or_league_fixture_notification,
)

logger = get_logger(__name__)

MESSAGE_TEXT_LIMIT = 3500


class NotifierBotCommandsHandler:
    def __init__(self):
        self._fixtures_db_manager: FixturesDBManager = FixturesDBManager()

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

    def available_leagues(self) -> List[str]:
        return self._fixtures_db_manager.get_all_leagues()

    def get_list_of_fitting_texts(
        self, list_of_texts: List[str], separator: str = f"\n"
    ) -> List[List[str]]:
        fitting_texts = []
        current_fitting_texts = []
        current_text = ""

        for text in list_of_texts:
            if len(f"{current_text}{separator}{text}") > MESSAGE_TEXT_LIMIT:
                fitting_texts.append(current_fitting_texts)
                current_text = ""
                current_fitting_texts = []
            else:
                current_text += f"{separator}{text}"
                current_fitting_texts.append(text)

        if current_fitting_texts:
            fitting_texts.append(current_fitting_texts)

        return [f"{separator}".join(texts) for texts in fitting_texts]

    def available_leagues_texts(self) -> List[str]:
        leagues = self.available_leagues()
        leagues_texts = [
            f"<strong>{league.id}</strong> - {league.name} ({league.country})"
            for league in leagues
        ]

        return self.get_list_of_fitting_texts(leagues_texts)

    @staticmethod
    def get_fixtures_text(
        converted_fixtures: List[Fixture], played: bool = False, with_date: bool = False
    ) -> List[str]:

        fixtures_text = ""
        all_fitting_fixtures = []
        current_fitting_fixtures = []

        for fixture in converted_fixtures:
            fixture_text = fixture.one_line_telegram_repr(played, with_date)

            if len(f"{fixtures_text}\n\n{fixture_text}") > MESSAGE_TEXT_LIMIT:
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

    def is_valid_id(self, id: Any) -> bool:
        try:
            int_id = int(id)
            return True
        except:
            return False


class SurroundingMatchesHandler(NotifierBotCommandsHandler):
    def __init__(self, commands_args: List[str], user: str, chat_id: str):
        super().__init__()
        self._command_args = commands_args
        self._teams = []
        self._leagues = []
        self._user = user
        self._chat_id = chat_id

    def validate_command_input(self) -> Optional[str]:
        if len(self._command_args):
            if str(self._command_args[0]).lower() in [
                "fteams",
                "ft",
                "favourite_teams",
            ]:
                self._teams = self._fixtures_db_manager.get_favourite_teams(
                    self._chat_id
                )
            elif str(self._command_args[0]).lower() in [
                "fleagues",
                "fl",
                "favourite_leagues",
            ]:
                self._leagues = self._fixtures_db_manager.get_favourite_leagues(
                    self._chat_id
                )
            else:
                self._leagues = self._command_args
        else:
            return (
                "You must enter:\n"
                " • At least one league\n"
                " • Or reference to you favourite teams (<em>fteams/ft/favourite_teams</em>) "
                "or leagues (<em>fleagues/fl/favourite_leagues</em>)"
            )

    def today_games(self) -> Tuple[str, str]:
        today_games_fixtures = (
            self._fixtures_db_manager.get_games_in_surrounding_n_days(
                0, leagues=self._leagues, teams=self._teams
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
            texts = [
                (
                    f"{Emojis.WAVING_HAND.value} Hi "
                    f"{self._user}, there were not matches found :("
                )
            ]
            photo = MESSI_PHOTO

        return (texts, photo)

    def yesterday_games(self) -> Tuple[str, str]:
        played_games_fixtures = (
            self._fixtures_db_manager.get_games_in_surrounding_n_days(
                -1, leagues=self._leagues, teams=self._teams
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
            texts = [
                (
                    f"{Emojis.WAVING_HAND.value} Hi "
                    f"{self._user}, there were not matches found :("
                )
            ]
            photo = MESSI_PHOTO

        return (texts, photo)

    def tomorrow_games(self) -> Tuple[str, str]:
        tomorrow_games_fixtures = (
            self._fixtures_db_manager.get_games_in_surrounding_n_days(
                1, leagues=self._leagues, teams=self._teams
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
            texts = [
                (
                    f"{Emojis.WAVING_HAND.value} Hi "
                    f"{self._user}, there were not matches found :("
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
            response = "You must enter a search text."
        else:
            team = " ".join(self._command_args)
            if len(team) < 4:
                response = "The search text should have at least <strong>4</strong> characters."

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
                f"Oops! There are no teams available with the search criteria '{team}'"
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
            response = f"Oops! There are no tournaments available with the search criteria '{league}'"

        return response


class NextAndLastMatchCommandHandler(NotifierBotCommandsHandler):
    def __init__(self, commands_args: List[str], user: str, chat_id: str) -> None:
        super().__init__()
        self._command_args = commands_args
        self._user = user
        self._team = None
        self._favourite_teams = []
        self._favourite_leagues = []
        self._chat_id = chat_id

    def validate_command_input(self) -> str:
        response = ""

        if len(self._command_args) < 1:
            response = "You must enter one argument."
        elif len(self._command_args) > 1:
            response = "You can only enter one argument."
        else:
            if str(self._command_args[0]).lower() in [
                "fteams",
                "ft",
                "favourite_teams",
            ]:
                self._favourite_teams = self._fixtures_db_manager.get_favourite_teams(
                    self._chat_id
                )
            elif str(self._command_args[0]).lower() in [
                "fleagues",
                "fl",
                "favourite_leagues",
            ]:
                self._favourite_leagues = (
                    self._fixtures_db_manager.get_favourite_leagues(self._chat_id)
                )
            else:
                self._team = self._command_args[0].lower()
                if not self.is_valid_id(self._team):
                    response = (
                        "You must enter a valid team id, the command doesn't work with team's name.\n"
                        "You can get your team's id by its name using /search_team command :)"
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
            telegram_next_team_or_league_fixture_notification(
                converted_fixture, team.name, self._user
            )
            if converted_fixture
            else ("There were not matches found.", None)
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
            telegram_last_team_or_league_fixture_notification(
                converted_fixture, team.name, self._user
            )
            if converted_fixture
            else ("There were not matches found.", None)
        )

    def upcoming_matches(self) -> Tuple[str, str]:
        team_id = self._command_args[0]

        if self._team:
            upcoming_fixtures = self._fixtures_db_manager.get_next_fixture(
                team_id=team_id, number_of_fixtures=5
            )
        elif self._favourite_teams:
            upcoming_fixtures = []
            for fav_team in self._favourite_teams:
                upcoming_fixtures += self._fixtures_db_manager.get_next_fixture(
                    team_id=fav_team
                )
        else:
            upcoming_fixtures = []
            for fav_league in self._favourite_leagues:
                upcoming_fixtures += self._fixtures_db_manager.get_next_fixture(
                    league_id=fav_league
                )

        if len(upcoming_fixtures):
            fixtures = remove_duplicate_fixtures(upcoming_fixtures)

            converted_fixtures = [convert_db_fixture(fixture) for fixture in fixtures]

            converted_fixtures.sort(key=lambda fixture: fixture.bsas_date)
            texts = self.get_fixtures_text(converted_fixtures, with_date=True)
            leagues = [fixture.championship for fixture in converted_fixtures]
            photo = random.choice([league.logo for league in leagues])
        else:
            texts = [
                (
                    f"{Emojis.WAVING_HAND.value} Hi "
                    f"{self._user}, unfortunately there are no matches found. :("
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
                f"{Emojis.WAVING_HAND.value} Hi {self._user}, "
                f"the last matches of {team.name} were:"
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
                    f"{Emojis.WAVING_HAND.value} Hi "
                    f"{self._user}, unfortunately there were not matches found for {team.name} :("
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
            response = "You must enter one tournament."
        elif len(self._command_args) > 1:
            response = "You must enter only one tournament."
        else:
            league = self._command_args[0]
            if not self.is_valid_id(league):
                response = (
                    "You must enter a valid league id, the command doesn't work with league's names.\n"
                    "You can get your league's id by its name using /search_league command :)"
                )

            if not self.is_available_league(league):
                response = f"Oops! '{league}' is not available :(\n"

        return response

    def next_match_league_notif(self) -> Tuple[str, str]:
        league_id = self._command_args[0]
        league = self._fixtures_db_manager.get_league(league_id)[0]

        next_league_db_fixture = self._fixtures_db_manager.get_next_fixture(
            league_id=league.id
        )

        converted_fixture = None

        if len(next_league_db_fixture):
            converted_fixture = convert_db_fixture(next_league_db_fixture[0])
            converted_fixture.head_to_head = get_head_to_heads(
                converted_fixture.home_team.id, converted_fixture.away_team.id
            )

        return (
            telegram_next_team_or_league_fixture_notification(
                converted_fixture, league.name, self._user
            )
            if converted_fixture
            else ("No matches were found.", None)
        )

    def last_match_league_notif(self) -> Tuple[str, str]:
        league_id = self._command_args[0]
        league = self._fixtures_db_manager.get_league(league_id)[0]

        last_league_db_fixture = self._fixtures_db_manager.get_last_fixture(
            league_id=league.id
        )

        converted_fixture = None

        if len(last_league_db_fixture):
            converted_fixture = convert_db_fixture(last_league_db_fixture[0])

        return (
            telegram_last_team_or_league_fixture_notification(
                converted_fixture, league.name, self._user
            )
            if converted_fixture
            else ("There were not matches found.", None)
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

            match_date = (
                "TODAY!"
                if converted_fixtures[0].bsas_date.date() == datetime.today().date()
                else f"on {Emojis.SPIRAL_CALENDAR.value} {converted_fixtures[0].bsas_date.strftime('%d-%m-%Y')}"
            )

            telegram_messages = self.get_fixtures_text(converted_fixtures)

            intro_text = (
                f"{Emojis.WAVING_HAND.value}Hi {self._user}! "
                f"\n\nThe next <strong>{league.name} ({league.country[:3].upper()})</strong> matches are {match_date}\n\n"
            )

            telegram_messages[0] = f"{intro_text}{telegram_messages[0]}"
        else:
            telegram_messages = ["There were not matches found."]

        return telegram_messages


class FavouriteTeamsCommandHandler(NotifierBotCommandsHandler):
    def __init__(
        self, commands_args: List[str], user: str, chat_id: str, is_list: bool = False
    ):
        super().__init__()
        self._command_args = commands_args
        self._user = user
        self._chat_id = chat_id
        self._is_list = is_list

    def validate_command_input(self) -> str:
        response = ""
        if len(self._command_args) < 1 and not self._is_list:
            response = "You must enter one team"
        elif len(self._command_args) > 1:
            response = "You must enter one team"
        else:
            if not self.is_valid_id(self._command_args[0]):
                response = (
                    "You must enter a valid team id, the command doesn't work with team's name.\n"
                    "You can get your team's id by its name using /search_team command :)"
                )

        return response

    def get_favourite_teams(self) -> str:
        favourite_teams = self._fixtures_db_manager.get_favourite_teams(self._chat_id)

        if len(favourite_teams):
            teams = [
                self._fixtures_db_manager.get_team(team)[0] for team in favourite_teams
            ]

            favourite_teams_texts = [
                f"<strong>{team.id}</strong> - {team.name}" for team in teams
            ]

            response = "\n".join(favourite_teams_texts)
        else:
            response = f"Oops! It seems you don't have favourite teams yet. Add them with <strong>/add_favourite_team</strong> command."

        return response

    def add_favourite_team(self) -> str:
        team_id = self._command_args[0]

        try:
            self._fixtures_db_manager.insert_favourite_team(team_id, self._chat_id)
            team = self._fixtures_db_manager.get_team(team_id)[0]
            response = f"Team '{team.name}' was added to your favourites successfully."
        except Exception as e:
            response = str(e)

        return response

    def delete_favourite_team(self) -> str:
        team_id = self._command_args[0]

        try:
            self._fixtures_db_manager.delete_favourite_team(team_id, self._chat_id)
            team = self._fixtures_db_manager.get_team(team_id)[0]
            response = (
                f"Team '{team.name}' was removed from your favourites successfully."
            )
        except Exception as e:
            response = str(e)

        return response


class FavouriteLeaguesCommandHandler(NotifierBotCommandsHandler):
    def __init__(
        self, commands_args: List[str], user: str, chat_id: str, is_list: bool = False
    ):
        super().__init__()
        self._command_args = commands_args
        self._user = user
        self._chat_id = chat_id
        self._is_list = is_list

    def validate_command_input(self) -> str:
        if len(self._command_args) < 1 and not self._is_list:
            response = "You must enter one league"
        elif len(self._command_args) > 1:
            response = "You must enter one league"
        else:
            league = self._command_args[0]
            if not self.is_valid_id(league):
                response = (
                    "You must enter a valid league id, the command doesn't work with league's names.\n"
                    "You can get your league's id by its name using /search_league command :)"
                )

            if not self.is_available_league(league):
                response = f"Oops! '{league}' is not available :(\n"
        return response

    def get_favourite_leagues(self) -> str:
        favourite_leagues = self._fixtures_db_manager.get_favourite_leagues(
            self._chat_id
        )

        if len(favourite_leagues):
            leagues = [
                self._fixtures_db_manager.get_league(league)[0]
                for league in favourite_leagues
            ]

            favourite_leagues_texts = [
                f"<strong>{league.id}</strong> - {league.name}" for league in leagues
            ]

            response = "\n".join(favourite_leagues_texts)
        else:
            response = (
                f"Oops! It seems you don't have favourite leagues yet. Add them with "
                f"<strong>/add_favourite_league</strong> command."
            )

        return response

    def add_favourite_league(self) -> str:
        league_id = self._command_args[0]

        try:
            self._fixtures_db_manager.insert_favourite_league(league_id, self._chat_id)
            league = self._fixtures_db_manager.get_league(league_id)[0]
            response = (
                f"League '{league.name}' was added to your favourites successfully."
            )
        except Exception as e:
            response = str(e)

        return response

    def delete_favourite_league(self) -> str:
        league_id = self._command_args[0]

        try:
            self._fixtures_db_manager.delete_favourite_league(league_id, self._chat_id)
            league = self._fixtures_db_manager.get_league(league_id)[0]
            response = (
                f"League '{league.name}' was removed from your favourites successfully."
            )
        except Exception as e:
            response = str(e)

        return response
