from typing import Any, List, Optional

from deep_translator import GoogleTranslator

from src.db.fixtures_db_manager import FixturesDBManager
from src.db.notif_sql_models import ConfigLanguage as DBConfigLanguage
from src.db.notif_sql_models import Fixture
from src.db.notif_sql_models import Language as DBLanguage
from src.db.notif_sql_models import League as DBLeague
from src.db.notif_sql_models import Team as DBTeam
from src.notifier_constants import ENGLISH_LANG_ID, TELEGRAM_MSG_LENGTH_LIMIT
from src.notifier_logger import get_logger

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
        teams = self._fixtures_db_manager.get_teams_by_name(team_text)
        if len(teams):
            for team in teams:
                team.country = (
                    self._fixtures_db_manager.get_country(team.country)[0].name
                    if team.country
                    else ""
                )
        return teams

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
                fixtures_text += "<not_translate>\n\n</not_translate>" + fixture_text
                logger.info(f"Appended fixture text -> {fixture_text}")
                current_fitting_fixtures.append(fixture)

        if current_fitting_fixtures:
            all_fitting_fixtures.append(current_fitting_fixtures)

        logger.info(f"All fitting fixtures: {all_fitting_fixtures}")

        return [
            "<not_translate>\n\n</not_translate>".join(
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
