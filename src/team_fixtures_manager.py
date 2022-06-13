import random
from datetime import datetime
from typing import List, Optional

from sqlmodel import or_, select

from config.notif_config import NotifConfig
from src.api.fixtures_client import FixturesClient
from src.db.db_manager import NotifierDBManager
from src.db.notif_sql_models import Fixture as DBFixture
from src.db.notif_sql_models import League as DBLeague
from src.db.notif_sql_models import Team as DBTeam
from src.emojis import Emojis
from src.entities import Fixture, TeamStanding
from src.senders.email_sender import send_email_html
from src.senders.telegram_sender import send_telegram_message
from src.utils.date_utils import get_date_spanish_text_format
from src.utils.fixtures_utils import (
    get_image_search,
    get_last_fixture,
    get_last_fixture_db,
    get_next_fixture,
    get_next_fixture_db,
    get_youtube_highlights_videos,
)
from src.utils.message_utils import (
    get_first_phrase_msg,
    get_team_intro_message,
    is_subscripted_for_team,
)


class TeamFixturesManager:
    def __init__(self, season: str, team_id: str) -> None:
        self._season = season
        self._team_id = team_id
        self._fixtures_client = FixturesClient()
        self._notifier_db_manager = NotifierDBManager()

    def get_next_team_fixture_text(self, user: str = "") -> tuple:
        next_team_fixture = self.get_next_team_fixture()
        return (
            self._telegram_next_fixture_notification(next_team_fixture, True, user)
            if next_team_fixture
            else ("Fixture para el equipo no encontrado", "")
        )

    def get_last_team_fixture_text(self, user: str = "") -> tuple:
        last_team_fixture = self.get_last_team_fixture()
        return (
            self._telegram_last_fixture_notification(last_team_fixture, user)
            if last_team_fixture
            else ("Fixture para el equipo no encontrado", "")
        )

    def get_next_team_fixture(self) -> Optional[Fixture]:
        fixtures_statement = select(DBFixture).where(
            or_(
                DBFixture.home_team == self._team_id,
                DBFixture.away_team == self._team_id,
            )
        )
        team_fixtures = self._notifier_db_manager.select_records(fixtures_statement)

        next_team_fixture = None

        if len(team_fixtures):
            next_team_fixture = get_next_fixture_db(team_fixtures)

        return next_team_fixture

    def notify_next_fixture_db(self) -> None:
        next_team_fixture = self.get_next_team_fixture()

        if next_team_fixture:
            if next_team_fixture.remaining_time().days < NotifConfig.NEXT_MATCH_THRESHOLD:
                self._perform_fixture_notification(next_team_fixture)

    def notify_next_fixture(self) -> None:
        team_fixtures = self._fixtures_client.get_fixtures_by(
            self._season, self._team_id
        )

        next_team_fixture = None

        if "response" in team_fixtures.as_dict:
            next_team_fixture = get_next_fixture(
                team_fixtures.as_dict["response"], self._team_id
            )

        if next_team_fixture:
            if next_team_fixture.remaining_time().days < 500:
                self._perform_fixture_notification(next_team_fixture)

    def notify_fixture_line_up_update(self) -> None:
        team_fixtures = self._fixtures_client.get_fixtures_by(
            self._season, self._team_id
        )

        next_team_fixture = None

        if "response" in team_fixtures.as_dict:
            next_team_fixture = get_next_fixture(
                team_fixtures.as_dict["response"], self._team_id
            )

        if next_team_fixture:
            if (
                next_team_fixture.remaining_time().days < 1
                and next_team_fixture.remaining_time().hours < 6
                and next_team_fixture.line_up
            ):
                self._perform_line_up_confirmed_notification(next_team_fixture)
            else:
                print(
                    f"There is still no line up for the match of {next_team_fixture.home_team} vs {next_team_fixture.away_team}"
                )
                print(str(next_team_fixture.remaining_time()))

    def get_last_team_fixture(self) -> Optional[Fixture]:
        fixtures_statement = select(DBFixture).where(
            or_(
                DBFixture.home_team == self._team_id,
                DBFixture.away_team == self._team_id,
            )
        )
        team_fixtures = self._notifier_db_manager.select_records(fixtures_statement)

        last_team_fixture = None

        if team_fixtures:
            last_team_fixture = get_last_fixture_db(team_fixtures)

        return last_team_fixture

    def notify_last_fixture_db(self) -> None:
        fixtures_statement = select(DBFixture).where(
            or_(
                DBFixture.home_team == self._team_id,
                DBFixture.away_team == self._team_id,
            )
        )
        team_fixtures = self._notifier_db_manager.select_records(fixtures_statement)

        last_team_fixture = None

        if team_fixtures:
            last_team_fixture = get_last_fixture_db(team_fixtures)

        if last_team_fixture:
            if (
                NotifConfig.LAST_MATCH_THRESHOLD_DAYS
                <= last_team_fixture.remaining_time().days
                <= 0
            ):
                self._perform_last_fixture_notification(last_team_fixture)

    def notify_last_fixture(self) -> None:
        team_fixtures = self._fixtures_client.get_fixtures_by(
            self._season, self._team_id
        )

        last_team_fixture = get_last_fixture(
            team_fixtures.as_dict["response"], self._team_id
        )

        if last_team_fixture:
            if (
                -1
                <= last_team_fixture.remaining_time().days
                <= NotifConfig.LAST_MATCH_THRESHOLD_DAYS
            ):
                last_team_fixture.highlights = get_youtube_highlights_videos(
                    last_team_fixture.home_team, last_team_fixture.away_team
                )
                self._perform_last_fixture_notification(last_team_fixture)

    def _telegram_last_fixture_notification(
        self, team_fixture: Fixture, user: str = ""
    ) -> tuple:
        match_images = self._get_match_images(team_fixture.championship.league_id)
        match_image_url = random.choice(match_images)
        spanish_format_date = get_date_spanish_text_format(team_fixture.bsas_date)

        team_intro_message = get_team_intro_message(
            team_fixture.home_team
            if str(team_fixture.home_team.id) == str(self._team_id)
            else team_fixture.away_team
        )["last_match"]

        highlights_yt_url = f"https://www.youtube.com/results?search_query={team_fixture.home_team.name}+vs+{team_fixture.away_team.name}+jugadas+resumen"
        highlights_text = f"{Emojis.FILM_PROJECTOR.value} <a href='{highlights_yt_url}'>HIGHLIGHTS</a>"

        telegram_message = (
            f"{Emojis.WAVING_HAND.value}Hola {user}!\n\n"
            f"{team_intro_message} "
            f"jugó el {spanish_format_date}! \nEste fue el resultado: \n\n"
            f"{team_fixture.matched_played_telegram_like_repr()}"
            f"{highlights_text}"
        )

        return (telegram_message, match_image_url)

    def _telegram_next_fixture_notification(
        self, team_fixture: Fixture, is_on_demand: False, user: str = ""
    ) -> tuple:
        spanish_format_date = get_date_spanish_text_format(team_fixture.bsas_date)
        match_images = self._get_match_images(team_fixture.championship.league_id)
        match_image_url = random.choice(match_images)
        date_text = (
            "es HOY!"
            if team_fixture.bsas_date.day == datetime.today().day
            else f"es el {Emojis.SPIRAL_CALENDAR.value} {spanish_format_date}."
        )

        first_phrase = get_first_phrase_msg(True, is_on_demand)
        team_intro_message = get_team_intro_message(
            team_fixture.home_team
            if str(team_fixture.home_team.id) == str(self._team_id)
            else team_fixture.away_team
        )["next_match"]

        intro_message = f"{first_phrase} {team_intro_message}"

        telegram_message = (
            f"{Emojis.WAVING_HAND.value}Hola {user}! "
            f"\n\n{intro_message} {date_text}\n\n{team_fixture.telegram_like_repr()}"
        )

        return (telegram_message, match_image_url)

    def _perform_last_fixture_notification(
        self, team_fixture: Fixture, team_standing: TeamStanding = None
    ) -> None:
        match_images = self._get_match_images(team_fixture.championship.league_id)
        match_image_url = random.choice(match_images)

        # telegram
        team_standing_msg = (
            f"{Emojis.RED_EXCLAMATION_MARK.value} Situación actual en el campeonato: \n\n{team_standing.telegram_like_repr()}\n"
            if team_standing
            else ""
        )

        team_intro_message = get_team_intro_message(
            team_fixture.home_team
            if str(team_fixture.home_team.id) == str(self._team_id)
            else team_fixture.away_team
        )["last_match"]

        highlights_yt_url = f"https://www.youtube.com/results?search_query={team_fixture.home_team.name}+vs+{team_fixture.away_team.name}+jugadas+resumen"
        highlights_text = f"{Emojis.FILM_PROJECTOR.value} <a href='{highlights_yt_url}'>HIGHLIGHTS</a>"

        FOOTBALL_TELEGRAM_RECIPIENTS = NotifConfig.TELEGRAM_RECIPIENTS
        for recipient in FOOTBALL_TELEGRAM_RECIPIENTS:
            if is_subscripted_for_team(recipient, self._team_id):
                telegram_message = (
                    f"{Emojis.WAVING_HAND.value}Hola {recipient.name}!\n\n"
                    f"{team_intro_message} "
                    f"jugó ayer! \nEste fue el resultado: \n\n"
                    f"{team_fixture.matched_played_telegram_like_repr()}"
                    f"\n{highlights_text}"
                )
                send_telegram_message(
                    recipient.telegram_id,
                    telegram_message,
                    match_image_url,
                )

        # email
        team_standing_email_msg = (
            f"Situación actual en el campeonato: \n\n{team_standing.email_like_repr()}"
            if team_standing
            else ""
        )
        match_image_text = f"<img src='{match_image_url}'>"
        email_standing_message = (
            f"{Emojis.RED_EXCLAMATION_MARK.value}{team_standing_email_msg}\n"
        )
        highlights_text = f"https://www.youtube.com/results?search_query={team_fixture.home_team.name}+vs+{team_fixture.away_team.name}+jugadas+resumen"

        EMAIL_RECIPIENTS = NotifConfig.EMAIL_RECIPIENTS
        for recipient in EMAIL_RECIPIENTS:
            message = (
                f"{Emojis.WAVING_HAND.value}Hola {recipient.name}!\n\n{team_intro_message} "
                f"jugó ayer!<br /><br />{match_image_text}<br /><br />Este fue el resultado: \n\n{team_fixture.matched_played_email_like_repr()}"
                f"<br /><br />{email_standing_message}<br /><br />{highlights_text}"
            )

            send_email_html(
                f"{team_fixture.home_team.name} ({team_fixture.match_score.home_score}) - "
                f"({team_fixture.match_score.away_score}) {team_fixture.away_team.name}",
                message,
                recipient.email,
            )

    def _perform_fixture_notification(self, team_fixture: Fixture) -> None:
        spanish_format_date = get_date_spanish_text_format(team_fixture.bsas_date)
        match_images = self._get_match_images(team_fixture.championship.league_id)
        match_image_url = random.choice(match_images)
        match_image_text = f"<img width='100%' height='100%' src='{match_image_url}'>"
        date_text = (
            "es HOY!"
            if team_fixture.bsas_date.day == datetime.today().day
            else f"es el {Emojis.SPIRAL_CALENDAR.value} {spanish_format_date}."
        )

        first_phrase = get_first_phrase_msg(True)
        team_intro_message = get_team_intro_message(
            team_fixture.home_team
            if str(team_fixture.home_team.id) == str(self._team_id)
            else team_fixture.away_team
        )["next_match"]

        intro_message = f"{first_phrase} {team_intro_message}"

        # telegram
        FOOTBALL_TELEGRAM_RECIPIENTS = NotifConfig.TELEGRAM_RECIPIENTS
        for recipient in FOOTBALL_TELEGRAM_RECIPIENTS:
            if is_subscripted_for_team(recipient, self._team_id):
                telegram_message = (
                    f"{Emojis.WAVING_HAND.value}Hola "
                    f"{recipient.name}!\n\n{intro_message} {date_text}\n\n{team_fixture.telegram_like_repr()}"
                )
                send_telegram_message(
                    recipient.telegram_id,
                    telegram_message,
                    photo=match_image_url,
                )

        # email
        EMAIL_RECIPIENTS = NotifConfig.EMAIL_RECIPIENTS
        for recipient in EMAIL_RECIPIENTS:
            message = f"{Emojis.WAVING_HAND.value}Hola {recipient.name}!\n\n{intro_message} {date_text}\n\n<br /><br />{match_image_text}<br /><br />{team_fixture.email_like_repr()}"
            send_email_html(
                f"{team_fixture.home_team.name} vs. {team_fixture.away_team.name}",
                message,
                recipient.email,
            )

    def _perform_line_up_confirmed_notification(self, team_fixture: Fixture) -> None:
        match_teams = f"{team_fixture.home_team.name} vs {team_fixture.away_team.name}"
        match_image_url = get_image_search(match_teams)
        match_image_text = f"<img src='{match_image_url}'>"

        # telegram
        FOOTBALL_TELEGRAM_RECIPIENTS = NotifConfig.TELEGRAM_RECIPIENTS
        for recipient in FOOTBALL_TELEGRAM_RECIPIENTS:
            intro_message = f"Se actualizó la alineación para {match_teams}:"
            telegram_message = f"{Emojis.WAVING_HAND.value}Hola {recipient.name}!\n\n{intro_message}\n\n{team_fixture.telegram_like_repr()}"
            send_telegram_message(
                recipient.telegram_id,
                telegram_message,
                photo=match_image_url,
            )

        # email
        EMAIL_RECIPIENTS = NotifConfig.EMAIL_RECIPIENTS
        for recipient in EMAIL_RECIPIENTS:
            message = f"{Emojis.WAVING_HAND.value}Hola {recipient.name}!\n\n{intro_message}\n\n<br /><br />{match_image_text}<br /><br />{team_fixture.email_like_repr()}"
            send_email_html(
                f"{team_fixture.home_team.name} vs. {team_fixture.away_team.name}",
                message,
                recipient.email,
            )

    def _get_match_images(self, league_id: int) -> List[str]:
        match_image_url_team_statement = select(DBTeam).where(
            DBTeam.id == self._team_id
        )
        match_image_url_league_statement = select(DBLeague).where(
            DBLeague.id == league_id
        )

        team_image_url = self._notifier_db_manager.select_records(
            match_image_url_team_statement
        )[0].picture
        league_image_url = self._notifier_db_manager.select_records(
            match_image_url_league_statement
        )[0].logo

        return [team_image_url, league_image_url]
