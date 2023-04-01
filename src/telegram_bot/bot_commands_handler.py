import random
from datetime import datetime
from typing import Any, List, Optional, Tuple

from deep_translator import GoogleTranslator

from src.db.fixtures_db_manager import FixturesDBManager
from src.db.notif_sql_models import ConfigLanguage as DBConfigLanguage
from src.db.notif_sql_models import FavouriteLeague, FavouriteTeam, Fixture
from src.db.notif_sql_models import Language as DBLanguage
from src.db.notif_sql_models import League as DBLeague
from src.db.notif_sql_models import Team as DBTeam
from src.emojis import Emojis, get_emoji_text_by_name
from src.notifier_constants import ENGLISH_LANG_ID, TELEGRAM_MSG_LENGTH_LIMIT
from src.notifier_logger import get_logger
from src.telegram_bot.bot_constants import MESSI_PHOTO
from src.utils.db_utils import remove_duplicate_fixtures
from src.utils.fixtures_utils import convert_db_fixture, get_head_to_heads
from src.utils.notification_text_utils import (
    telegram_last_team_or_league_fixture_notification,
    telegram_next_team_or_league_fixture_notification,
)

logger = get_logger(__name__)


class NotifierBotCommandsHandler:
    def __init__(self, chat_id: str = ""):
        self._fixtures_db_manager: FixturesDBManager = FixturesDBManager()
        self._chat_id = str(chat_id)
        self._language: DBLanguage = self.get_user_language(self._chat_id)

    def get_user_language(self, chat_id: str) -> DBLanguage:
        try:
            config_language: DBConfigLanguage = (
                self._fixtures_db_manager.get_config_language(str(chat_id))[0]
            )
        except IndexError:
            self._fixtures_db_manager.insert_or_update_user_config_language(
                lang_id=ENGLISH_LANG_ID, chat_id=self._chat_id
            )
            config_language = self._fixtures_db_manager.get_config_language(
                str(chat_id)
            )[0]

        return self._fixtures_db_manager.get_language_by_id(config_language.lang_id)[0]

    def search_team(self, team_text: str) -> Optional[DBTeam]:
        return self._fixtures_db_manager.get_teams_by_name(team_text)

    def search_league(self, league_text: str) -> Optional[DBLeague]:
        return self._fixtures_db_manager.get_leagues_by_name(league_text)

    def search_leagues_by_country(self, country_text: str) -> Optional[DBLeague]:
        return self._fixtures_db_manager.get_leagues_by_country(country_text)

    def search_time_zone(self, time_zone_text: str) -> Optional[DBTeam]:
        return self._fixtures_db_manager.get_time_zones_by_name(time_zone_text)

    def search_language(self, language_text: str) -> Optional[DBLanguage]:
        return self._fixtures_db_manager.get_languages_by_name(language_text)

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
            if len(f"{current_text}{separator}{text}") > TELEGRAM_MSG_LENGTH_LIMIT:
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
            f"<strong>{league.id}</strong> - {league.name}{self._get_country_text(league.country)}"
            for league in leagues
        ]

        return self.get_list_of_fitting_texts(leagues_texts)

    def _get_country_text(self, country: str) -> str:
        return f"({country[:3].upper()})" if country.lower() != "world" else ""

    @staticmethod
    def get_fixtures_text(
        converted_fixtures: List[Fixture], played: bool = False, with_date: bool = False
    ) -> List[str]:
        fixtures_text = ""
        all_fitting_fixtures = []
        current_fitting_fixtures = []

        for fixture in converted_fixtures:
            fixture_text = fixture.one_line_telegram_repr(played, with_date)

            if len(f"{fixtures_text}\n\n{fixture_text}") > TELEGRAM_MSG_LENGTH_LIMIT:
                all_fitting_fixtures.append(current_fitting_fixtures)
                fixtures_text = ""
                current_fitting_fixtures = []
            else:
                fixtures_text += "\n\n" + fixture_text
                logger.info(f"Appended fixture text -> {fixture_text}")
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

    def text_to_user_language(self, text: str) -> str:
        google_translator = GoogleTranslator(
            source="en", target=self._language.short_name
        )
        return google_translator.translate(text)

    def is_valid_id(self, id: Any) -> bool:
        try:
            int_id = int(id)
            return True
        except:
            return False

    def get_user_main_time_zone(self) -> str:
        time_zones = self._fixtures_db_manager.get_user_time_zones(self._chat_id)
        main_time_zone = ""

        if len(time_zones):
            main_time_zone = [
                time_zone for time_zone in time_zones if time_zone.is_main_tz
            ]

            if len(main_time_zone):
                main_time_zone = main_time_zone[0]

        return (
            self._fixtures_db_manager.get_time_zone(main_time_zone.time_zone)[0].name
            if main_time_zone
            else "UTC"
        )


class SurroundingMatchesHandler(NotifierBotCommandsHandler):
    def __init__(self, commands_args: List[str], user: str, chat_id: str):
        super().__init__(chat_id)
        self._command_args = commands_args
        self._teams = []
        self._leagues = []
        self._user = user
        self._user_time_zones = self._fixtures_db_manager.get_user_time_zones(
            self._chat_id
        )
        self._user_main_time_zone = self.get_user_main_time_zone()

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
            self._fixtures_db_manager.get_surround_games_in_time_zone(
                "today",
                leagues=self._leagues,
                teams=self._teams,
                time_zone=self._user_main_time_zone,
            )
        )

        if len(today_games_fixtures):
            converted_games = [
                convert_db_fixture(fixture, self._user_time_zones)
                for fixture in today_games_fixtures
            ]
            texts = self.get_fixtures_text(converted_games)
            leagues = [fixture.championship for fixture in converted_games]
            photo = random.choice([league.logo for league in leagues])
        else:
            texts = [
                self.text_to_user_language(
                    f"{Emojis.WAVING_HAND.value} Hi "
                    f"{self._user}, there were not matches found :("
                )
            ]
            photo = MESSI_PHOTO

        return (texts, photo)

    def yesterday_games(self) -> Tuple[str, str]:
        played_games_fixtures = (
            self._fixtures_db_manager.get_surround_games_in_time_zone(
                "yesterday",
                leagues=self._leagues,
                teams=self._teams,
                time_zone=self._user_main_time_zone,
            )
        )

        if len(played_games_fixtures):
            converted_fixtures = [
                convert_db_fixture(fixture, self._user_time_zones)
                for fixture in played_games_fixtures
            ]
            texts = self.get_fixtures_text(converted_fixtures, played=True)
            leagues = [fixture.championship for fixture in converted_fixtures]
            photo = random.choice([league.logo for league in leagues])
        else:
            texts = [
                self.text_to_user_language(
                    f"{Emojis.WAVING_HAND.value} Hi "
                    f"{self._user}, there were not matches found :("
                )
            ]
            photo = MESSI_PHOTO

        return (texts, photo)

    def tomorrow_games(self) -> Tuple[str, str]:
        tomorrow_games_fixtures = (
            self._fixtures_db_manager.get_surround_games_in_time_zone(
                "tomorrow",
                leagues=self._leagues,
                teams=self._teams,
                time_zone=self._user_main_time_zone,
            )
        )

        if len(tomorrow_games_fixtures):
            converted_fixtures = [
                convert_db_fixture(fixture, self._user_time_zones)
                for fixture in tomorrow_games_fixtures
            ]
            texts = self.get_fixtures_text(converted_fixtures)
            leagues = [fixture.championship for fixture in converted_fixtures]
            photo = random.choice([league.logo for league in leagues])
        else:
            texts = [
                self.text_to_user_language(
                    f"{Emojis.WAVING_HAND.value} Hi "
                    f"{self._user}, there were not matches found :("
                )
            ]
            photo = MESSI_PHOTO

        return (texts, photo)


class SearchCommandHandler(NotifierBotCommandsHandler):
    def __init__(self, commands_args: List[str], user: str):
        super().__init__()
        self._command_args = commands_args
        self._user = user

    def validate_command_input(self) -> str:
        response = ""
        if len(self._command_args) < 1:
            response = "You must enter a search text. For example '/search_team barcelona' or '/search_league premier'"
        else:
            team = " ".join(self._command_args)
            if len(team) < 3:
                response = "The search text should have at least <strong>3</strong> characters."

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
            response = self._found_leagues_notif(found_leagues)
        else:
            response = f"Oops! There are no tournaments available with the search criteria '{league}'"

        return response

    def search_leagues_by_country_notif(self) -> str:
        country = " ".join(self._command_args)

        found_leagues = self.search_leagues_by_country(country)

        if found_leagues:
            response = self._found_leagues_notif(found_leagues)
        else:
            response = f"Oops! There are no tournaments available with the country search criteria '{country}'"

        return response

    @staticmethod
    def _found_leagues_notif(found_leagues: list) -> str:
        found_teams_texts = [
            f"<strong>{league.id}</strong> - {league.name} ({league.country[:3].upper()})"
            for league in found_leagues
        ]

        return "\n".join(found_teams_texts)

    def search_time_zone_notif(self) -> str:
        time_zone_text = " ".join(self._command_args)

        found_time_zones = self.search_time_zone(time_zone_text)

        if found_time_zones:
            found_time_zones_texts = []
            for time_zone in found_time_zones:
                emoji_text = (
                    get_emoji_text_by_name(time_zone.emoji) if time_zone.emoji else ""
                )
                found_time_zones_texts.append(
                    f"<strong>{time_zone.id}</strong> - {time_zone.name} {emoji_text}"
                )

            response = "\n".join(found_time_zones_texts)
        else:
            response = f"Oops! There are no time zones available with the search criteria '{time_zone_text}'"

        return response


class NextAndLastMatchCommandHandler(NotifierBotCommandsHandler):
    def __init__(self, commands_args: List[str], user: str, chat_id: str) -> None:
        super().__init__(chat_id)
        self._command_args = commands_args
        self._user = user
        self._team = None
        self._favourite_teams = []
        self._favourite_leagues = []

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
            user_time_zones = self._fixtures_db_manager.get_user_time_zones(
                self._chat_id
            )
            converted_fixture = convert_db_fixture(
                next_team_db_fixture[0], user_time_zones=user_time_zones
            )
            converted_fixture.head_to_head = get_head_to_heads(
                converted_fixture.home_team.id, converted_fixture.away_team.id
            )

        return (
            telegram_next_team_or_league_fixture_notification(
                converted_fixture, team.name, self._user, self.get_user_main_time_zone()
            )
            if converted_fixture
            else (self.text_to_user_language("There were not matches found."), None)
        )

    def last_match_team_notif(self) -> Tuple[str, str]:
        team_id = self._command_args[0]
        team = self._fixtures_db_manager.get_team(team_id)[0]

        last_team_db_fixture = self._fixtures_db_manager.get_last_fixture(
            team_id=team_id
        )

        converted_fixture = None

        if len(last_team_db_fixture):
            user_time_zones = self._fixtures_db_manager.get_user_time_zones(
                self._chat_id
            )
            converted_fixture = convert_db_fixture(
                last_team_db_fixture[0], user_time_zones=user_time_zones
            )

        return (
            telegram_last_team_or_league_fixture_notification(
                converted_fixture, team.name, self._user, self.get_user_main_time_zone()
            )
            if converted_fixture
            else (self.text_to_user_language("There were not matches found."), None)
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
            user_time_zones = self._fixtures_db_manager.get_user_time_zones(
                self._chat_id
            )

            fixtures = remove_duplicate_fixtures(upcoming_fixtures)

            converted_fixtures = [
                convert_db_fixture(fixture, user_time_zones) for fixture in fixtures
            ]

            converted_fixtures.sort(key=lambda fixture: fixture.bsas_date)
            texts = self.get_fixtures_text(converted_fixtures, with_date=True)
            leagues = [fixture.championship for fixture in converted_fixtures]
            photo = random.choice([league.logo for league in leagues])
        else:
            texts = [
                self.text_to_user_language(
                    f"{Emojis.WAVING_HAND.value} Hi "
                    f"{self._user}, unfortunately there are no matches found. :("
                )
            ]
            photo = MESSI_PHOTO

        return (texts, photo)

    def last_matches(self) -> Tuple[str, str]:
        team_id = self._command_args[0]

        if not self.is_valid_id(team_id):
            return (
                [
                    (
                        "You must enter a valid team id, the command doesn't work with team's name.\n"
                        "You can get your team's id by its name using /search_team command :)"
                    )
                ],
                "",
            )

        try:
            team = self._fixtures_db_manager.get_team(team_id)[0]
        except IndexError:
            return (
                [self.text_to_user_language("No team was found for the given id.")],
                "",
            )

        last_team_fixtures = self._fixtures_db_manager.get_last_fixture(
            team_id=team_id, number_of_fixtures=5
        )

        if len(last_team_fixtures):
            user_time_zones = self._fixtures_db_manager.get_user_time_zones(
                self._chat_id
            )
            converted_fixtures = [
                convert_db_fixture(fixture, user_time_zones)
                for fixture in last_team_fixtures
            ]
            introductory_text = self.text_to_user_language(
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
                self.text_to_user_language(
                    f"{Emojis.WAVING_HAND.value} Hi "
                    f"{self._user}, unfortunately there were not matches found for {team.name} :("
                )
            ]
            photo = MESSI_PHOTO

        return (texts, photo)


class NextAndLastMatchLeagueCommandHandler(NotifierBotCommandsHandler):
    def __init__(self, commands_args: List[str], user: str, chat_id: str):
        super().__init__(chat_id)
        self._command_args = commands_args
        self._user = user
        self._chat_id = chat_id
        self._user_time_zones = self._fixtures_db_manager.get_user_time_zones(
            self._chat_id
        )

    def validate_command_input(self) -> str:
        response = ""

        if len(self._command_args) < 1:
            response = self.text_to_user_language("You must enter one tournament.")
        elif len(self._command_args) > 1:
            response = self.text_to_user_language("You must enter only one tournament.")
        else:
            league = self._command_args[0]
            if not self.is_valid_id(league):
                response_text = self.text_to_user_language(
                    "You must enter a valid league id, the command doesn't work with league's names.\nYou can get your league's id by its name using"
                )
                response = f"{response_text} /search_league"

            if not self.is_available_league(league):
                response = f"Oops! '{league}' {self.text_to_user_language('is not available')} :(\n"

        return response

    def next_match_league_notif(self) -> Tuple[str, str]:
        league_id = self._command_args[0]

        try:
            league = self._fixtures_db_manager.get_league(league_id)[0]
        except IndexError:
            return ("No league was found for the given id.", "")

        next_league_db_fixture = self._fixtures_db_manager.get_next_fixture(
            league_id=league.id
        )

        converted_fixture = None

        if len(next_league_db_fixture):
            converted_fixture = convert_db_fixture(
                next_league_db_fixture[0], user_time_zones=self._user_time_zones
            )
            converted_fixture.head_to_head = get_head_to_heads(
                converted_fixture.home_team.id, converted_fixture.away_team.id
            )

        return (
            telegram_next_team_or_league_fixture_notification(
                converted_fixture,
                league.name,
                self._user,
                self.get_user_main_time_zone(),
            )
            if converted_fixture
            else ("No matches were found.", None)
        )

    def last_match_league_notif(self) -> Tuple[str, str]:
        league_id = self._command_args[0]

        try:
            league = self._fixtures_db_manager.get_league(league_id)[0]
        except IndexError:
            return ("No league was found for the given id.", "")

        last_league_db_fixture = self._fixtures_db_manager.get_last_fixture(
            league_id=league.id
        )

        converted_fixture = None

        if len(last_league_db_fixture):
            converted_fixture = convert_db_fixture(
                last_league_db_fixture[0], user_time_zones=self._user_time_zones
            )

        return (
            telegram_last_team_or_league_fixture_notification(
                converted_fixture,
                league.name,
                self._user,
                self.get_user_main_time_zone(),
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
            next_match_date = next_league_db_fixture.utc_date[:10]
            next_matches = self._fixtures_db_manager.get_fixtures_by_league(
                league.id, next_match_date
            )

            converted_fixtures = [
                convert_db_fixture(fixture, user_time_zones=self._user_time_zones)
                for fixture in next_matches
            ]

            match_date = (
                "TODAY!"
                if converted_fixtures[0].get_time_in_main_zone().date()
                == datetime.today().date()
                else f"on {Emojis.SPIRAL_CALENDAR.value} {converted_fixtures[0].get_time_in_main_zone().strftime('%A')[:3]}. {converted_fixtures[0].get_time_in_main_zone().strftime('%d-%m-%Y')}"
            )

            telegram_messages = self.get_fixtures_text(converted_fixtures)

            country_text = (
                f"({league.country[:3].upper()})"
                if league.country.lower() != "world"
                else ""
            )

            intro_text = (
                f"{Emojis.WAVING_HAND.value}Hi {self._user}! "
                f"\n\nThe next <strong>{league.name}{country_text}</strong> matches are {match_date}\n\n"
            )

            telegram_messages[0] = f"{intro_text}{telegram_messages[0]}"
        else:
            telegram_messages = ["There were not matches found."]

        return telegram_messages


class FavouriteTeamsCommandHandler(NotifierBotCommandsHandler):
    def __init__(
        self, commands_args: List[str], user: str, chat_id: str, is_list: bool = False
    ):
        super().__init__(chat_id)
        self._command_args = commands_args
        self._user = user
        self._is_list = is_list

    def validate_command_input(self) -> str:
        response = ""

        if not self._is_list:
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

    def get_favourite_teams(self) -> List[FavouriteTeam]:
        favourite_teams = self._fixtures_db_manager.get_favourite_teams(self._chat_id)
        return [
            self._fixtures_db_manager.get_team(team_id)[0]
            for team_id in favourite_teams
        ]

    def get_favourite_teams_response(self) -> str:
        favourite_teams = self.get_favourite_teams()
        if len(favourite_teams):
            teams = [
                self._fixtures_db_manager.get_team(team.id)[0]
                for team in favourite_teams
            ]

            favourite_teams_texts = [f"<strong>{team.name}</strong>" for team in teams]

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
        response = ""

        if not self._is_list:
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
                elif not self.is_available_league(league):
                    response = f"Oops! '{league}' is not available :(\n"
        return response

    def get_favourite_leagues(self) -> List[FavouriteLeague]:
        favourite_leagues = self._fixtures_db_manager.get_favourite_leagues(
            self._chat_id
        )
        return [
            self._fixtures_db_manager.get_league(league_id)[0]
            for league_id in favourite_leagues
        ]

    def get_favourite_leagues_response(self) -> str:
        favourite_leagues = self.get_favourite_leagues()

        if len(favourite_leagues):
            favourite_leagues_texts = [
                f"<strong>{league.name}</strong>" for league in favourite_leagues
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


class LanguagesCommandHandler(NotifierBotCommandsHandler):
    def __init__(self, user: str, chat_id: str, is_list: bool = False):
        super().__init__(chat_id)
        self._user = user
        self._is_list = is_list

    def get_config_language(self) -> str:
        user_config_language = self._fixtures_db_manager.get_config_language(
            self._chat_id
        )

        if len(user_config_language):
            language = self._fixtures_db_manager.get_language_by_id(
                user_config_language[0].lang_id
            )[0]
            return f"<strong>{language.name.capitalize()}</strong>"

        return f"Oops! It seems you don't have a language configured yet, you can do it with /set_language command."

    def set_language(self, lang_id: int) -> str:
        try:
            self._fixtures_db_manager.insert_or_update_user_config_language(
                lang_id, self._chat_id
            )
            language = self._fixtures_db_manager.get_language_by_id(lang_id)[0]
            response = f"You have set '{language.name.capitalize()}' as your language. From now on notifications and my responses will be sent in that language."
        except Exception as e:
            response = str(e)

        return response


class TimeZonesCommandHandler(NotifierBotCommandsHandler):
    def __init__(
        self, commands_args: List[str], user: str, chat_id: str, is_list: bool = False
    ):
        super().__init__(chat_id)
        self._command_args = commands_args
        self._user = user
        self._is_list = is_list

    def validate_command_input(self) -> str:
        response = ""

        if not self._is_list:
            if len(self._command_args) < 1 and not self._is_list:
                response = "You must enter one time zone"
            elif len(self._command_args) > 1:
                response = "You must enter one time zone"
            else:
                if not self.is_valid_id(self._command_args[0]):
                    response = (
                        "You must enter a valid time zone id, the command doesn't work with time zone's name.\n"
                        "You can get your time zone's id by its name using /search_time_zone command :)"
                    )

        return response

    def get_time_zones(self):
        user_time_zones = self._fixtures_db_manager.get_user_time_zones(self._chat_id)

        return [
            self._fixtures_db_manager.get_time_zone(user_tz.time_zone)[0]
            for user_tz in user_time_zones
        ]

    def get_my_time_zones(self) -> str:
        user_time_zones = self._fixtures_db_manager.get_user_time_zones(self._chat_id)

        if len(user_time_zones):
            user_time_zones_texts = []
            for user_time_zone in user_time_zones:
                time_zone = self._fixtures_db_manager.get_time_zone(
                    user_time_zone.time_zone
                )[0]
                emoji_text = (
                    f" {get_emoji_text_by_name(time_zone.emoji)}"
                    if time_zone.emoji
                    else ""
                )
                user_time_zones_texts.append(
                    f"<strong>{time_zone.id}</strong> - {time_zone.name}{emoji_text} {'(main)' if user_time_zone.is_main_tz else ''}"
                )

            response = "\n".join(user_time_zones_texts)
        else:
            response = (
                f"Oops! It seems you don't have time zones yet. This mean that by default you are using UTC as time zone."
                f"\nYou can add your main and additional time zones with <strong>/set_main_time_zone</strong> and "
                f"<strong>/set_add_time_zone</strong> commands."
            )

        return response

    def add_time_zone(self, main: str = False) -> str:
        time_zone_id = self._command_args[0]

        try:
            self._fixtures_db_manager.insert_user_time_zone(
                time_zone_id, self._chat_id, main=main
            )
            time_zone = self._fixtures_db_manager.get_time_zone(time_zone_id)[0]
            main_time_zone_text = " as your main time zone" if main else " time zone"
            response = (
                f"You have added '{time_zone.name}'{main_time_zone_text} successfully."
            )
        except Exception as e:
            response = str(e)

        return response

    def delete_time_zone(self) -> str:
        time_zone_id = self._command_args[0]

        try:
            self._fixtures_db_manager.delete_user_time_zone(time_zone_id, self._chat_id)
            response = f"Time zone was removed from your configured ones successfully."
        except Exception as e:
            response = str(e)

        return response


class NotifConfigCommandHandler(NotifierBotCommandsHandler):
    def __init__(
        self, commands_args: List[str], user: str, chat_id: str, is_list: bool = False
    ):
        super().__init__(chat_id)
        self._command_args = commands_args
        self._user = user
        self._is_list = is_list
        self._notif_type_id = None

    def validate_command_input(self) -> str:
        response = ""

        if not self._is_list:
            if len(self._command_args) < 1 and not self._is_list:
                response = "You must enter one notification type."
            elif len(self._command_args) > 1:
                response = "You must enter one notification type"
            else:
                if not self.is_valid_id(self._command_args[0]):
                    response = (
                        f"{Emojis.RED_EXCLAMATION_MARK.value} You must enter a valid notification type id.\n\n"
                        "You can get the notification type id using the /notif_config command :)"
                    )
                self._notif_type_id = self._command_args[0]

        return response

    def subscribe_to_notifications(self) -> str:
        existing_subscriptions = self._fixtures_db_manager.get_user_notif_config(
            self._chat_id
        )

        if len(existing_subscriptions):
            return f"You are already subscribed to notifications, so you can manage them through /notif_config."

        notif_types = self._fixtures_db_manager.get_all_notif_types()

        for notif_type in notif_types:
            self._fixtures_db_manager.insert_or_update_user_notif_config(
                notif_type.id, self._chat_id
            )

        return f"{Emojis.PARTYING_FACE.value} You have successfully subscribed to notifications! \n\n{Emojis.RIGHT_FACING_FIST.value} From now on you can manage them through /notif_config, /enable_notif_config and /disable_notif_config commands."

    def disable_notification(self) -> str:
        existing_subscriptions = self._fixtures_db_manager.get_user_notif_config(
            self._chat_id
        )

        if int(self._notif_type_id) not in [
            notif_config.notif_type for notif_config in existing_subscriptions
        ]:
            return "The provided notification type does not exist. Please check the available ones with /notif_config command."

        self._fixtures_db_manager.insert_or_update_user_notif_config(
            self._notif_type_id, self._chat_id, False
        )

        notif_type = self._fixtures_db_manager.get_notif_type(self._notif_type_id)[0]

        return f"You have successfully disabled '{notif_type.name}' notification. You can re-enable it at any time with /enable_notif_config command."

    def enable_notification(self) -> str:
        existing_subscriptions = self._fixtures_db_manager.get_user_notif_config(
            self._chat_id
        )

        if int(self._notif_type_id) not in [
            int(notif_config.notif_type) for notif_config in existing_subscriptions
        ]:
            return "The provided notification type does not exist. Please check the available ones with /notif_config command."

        self._fixtures_db_manager.insert_or_update_user_notif_config(
            self._notif_type_id, self._chat_id, True
        )

        notif_type = self._fixtures_db_manager.get_notif_type(self._notif_type_id)[0]

        return f"You have successfully enabled '{notif_type.name}' notification. You can disable it at any time with /disable_notif_config command."

    def notif_config(self) -> str:
        existing_subscriptions = self._fixtures_db_manager.get_user_notif_config(
            self._chat_id
        )

        if not len(existing_subscriptions):
            return f"{Emojis.RED_EXCLAMATION_MARK.value} You are not subscribed to notifications yet. \n\nPlease subscribe with /subscribe_to_notifications command first."

        notifications_config_text = ""

        for subscription in existing_subscriptions:
            notif_type = self._fixtures_db_manager.get_notif_type(
                subscription.notif_type
            )[0]
            status = (
                Emojis.CHECK_MARK_BUTTON.value
                if subscription.status
                else Emojis.NO_ENTRY.value
            )

            time_text = ""

            if notif_type.id in [1, 2]:
                time_text = f" ({subscription.time})"

            notifications_config_text += f"<strong>{notif_type.id} - {notif_type.name}</strong>{time_text} <em>{status}</em> - {notif_type.description}\n"

        return notifications_config_text

    def set_daily_notification_time(self) -> str:
        time = self._command_args[0]
        existing_subscriptions = self._fixtures_db_manager.get_user_notif_config(
            self._chat_id
        )
        user_main_time_zone = self.get_user_main_time_zone()

        if not len(existing_subscriptions):
            return (
                f"{Emojis.RED_EXCLAMATION_MARK.value} You are not subscribed to notifications yet. \n\nPlease "
                f"subscribe with /subscribe_to_notifications command first."
            )

        daily_subscriptions = [
            sub for sub in existing_subscriptions if sub.notif_type in [1, 2]
        ]

        for daily_sub in daily_subscriptions:
            daily_sub.time = time
            self._fixtures_db_manager.insert_or_update_user_notif_config(
                notif_type=daily_sub.notif_type,
                chat_id=daily_sub.chat_id,
                status=daily_sub.status,
                time=daily_sub.time,
            )

        return (
            f"{Emojis.CHECK_MARK_BUTTON.value} Your daily notifications have been set at <strong>{time}</strong>"
            f" in your main time zone ({user_main_time_zone}) succesfully!"
        )
