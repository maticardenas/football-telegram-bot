import random
from datetime import datetime
from typing import List

from sqlmodel import or_, select

from config.notif_config import NotifConfig
from db.db_manager import NotifierDBManager
from src.api.fixtures_client import FixturesClient
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
    get_team_standings_for_league,
    get_youtube_highlights_videos,
)
from src.utils.message_utils import (
    get_highlights_text,
    get_team_intro_messages,
    is_subscripted_for_team,
)


class TeamFixturesManager:
    def __init__(self, season: str, team_id: str) -> None:
        self._season = season
        self._team_id = team_id
        self._fixtures_client = FixturesClient()
        self._notifier_db_manager = NotifierDBManager()

    def notify_next_fixture_db(self) -> None:
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

        if next_team_fixture:
            if next_team_fixture.remaining_time().days < 500:
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

    def notify_last_fixture_db(self) -> None:
        fixtures_statement = select(DBFixture).where(
            or_(
                DBFixture.home_team == self._team_id,
                DBFixture.away_team == self._team_id,
            )
        )
        team_fixtures = self._notifier_db_manager.select_records(fixtures_statement)

        if team_fixtures:
            last_team_fixture = get_last_fixture_db(team_fixtures)

        if last_team_fixture:
            if (
                -40
                <= last_team_fixture.remaining_time().days
                <= NotifConfig.LAST_MATCH_THRESHOLD_DAYS
            ):
                # last_team_fixture.highlights = get_youtube_highlights_videos(
                #     last_team_fixture.home_team, last_team_fixture.away_team
                # )
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
                self._perform_last_fixture_notification(
                    last_team_fixture, team_league_standing
                )

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
        intro_message = get_team_intro_messages(
            self._team_id, is_group_notification=True
        )["last_match"]

        highlights_text = ""  # get_highlights_text(team_fixture.highlights)

        FOOTBALL_TELEGRAM_RECIPIENTS = NotifConfig.TELEGRAM_RECIPIENTS
        for recipient in FOOTBALL_TELEGRAM_RECIPIENTS:
            if is_subscripted_for_team(recipient, self._team_id):
                telegram_message = (
                    f"{Emojis.WAVING_HAND.value}Hola {recipient.name}!\n\n"
                    f"{intro_message} "
                    f"jugó ayer! \nEste fue el resultado: \n\n"
                    f"{team_fixture.matched_played_telegram_like_repr()}"
                    f"\n\n{team_standing_msg}\n{highlights_text}"
                )
                send_telegram_message(
                    recipient.telegram_id,
                    telegram_message,
                    match_image_url,
                )

        # email
        intro_message = get_team_intro_messages(self._team_id)["last_match"]
        team_standing_email_msg = (
            f"Situación actual en el campeonato: \n\n{team_standing.email_like_repr()}"
            if team_standing
            else ""
        )
        match_image_text = f"<img src='{match_image_url}'>"
        email_standing_message = (
            f"{Emojis.RED_EXCLAMATION_MARK.value}{team_standing_email_msg}\n"
        )
        highlights_text = ""  # get_highlights_text(team_fixture.highlights, email=True)

        EMAIL_RECIPIENTS = NotifConfig.EMAIL_RECIPIENTS
        for recipient in EMAIL_RECIPIENTS:
            message = (
                f"{Emojis.WAVING_HAND.value}Hola {recipient.name}!\n\n{intro_message} "
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

        # telegram
        FOOTBALL_TELEGRAM_RECIPIENTS = NotifConfig.TELEGRAM_RECIPIENTS
        for recipient in FOOTBALL_TELEGRAM_RECIPIENTS:
            if is_subscripted_for_team(recipient, self._team_id):
                intro_message = get_team_intro_messages(
                    self._team_id, is_group_notification=True
                )["next_match"]
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
            intro_message = get_team_intro_messages(self._team_id)["next_match"]
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
            intro_message = get_team_intro_messages(self._team_id)["next_match"]
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
