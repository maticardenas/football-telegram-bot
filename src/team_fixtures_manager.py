from datetime import datetime

from config.email_notif import EMAIL_RECIPIENTS
from config.telegram_notif import TELEGRAM_RECIPIENTS
from config.whatsapp_notif import RECIPIENTS
from src.api.fixtures_client import FixturesClient
from src.emojis import Emojis
from src.entities import Fixture, TeamStanding
from src.senders.email_sender import send_email_html
from src.senders.telegram_sender import send_telegram_message
from src.senders.whatsapp_sender import send_whatsapp_message
from src.utils.date_utils import get_date_spanish_text_format
from src.utils.fixtures_utils import (
    get_last_fixture,
    get_next_fixture,
    get_team_standings_for_league, get_image_search,
)


class TeamFixturesManager:
    def __init__(self, season: str, team_id: str) -> None:
        self._season = season
        self._team_id = team_id
        self._fixtures_client = FixturesClient()
        self._team_logo = self._get_team_logo()

    def _get_team_logo(self) -> str:
        team_info = self._fixtures_client.get_team_information(self._team_id)
        return team_info.as_dict["response"][0]["team"]["logo"]

    def notify_next_fixture(self) -> None:
        team_fixtures = self._fixtures_client.get_fixtures_by(
            self._season, self._team_id
        )

        next_team_fixture = get_next_fixture(team_fixtures.as_dict["response"])

        if next_team_fixture:
            if next_team_fixture.remaining_time().days < 3:
                self._perform_fixture_notification(next_team_fixture)

    def notify_last_fixture(self) -> None:
        team_fixtures = self._fixtures_client.get_fixtures_by(
            self._season, self._team_id
        )

        last_team_fixture = get_last_fixture(team_fixtures.as_dict["response"])

        if last_team_fixture:
            team_standings = self._fixtures_client.get_standings_by(
                self._season, self._team_id
            )
            team_league_standing = get_team_standings_for_league(
                team_standings.as_dict["response"], last_team_fixture.championship.league_id
            )
            if -1 <= last_team_fixture.remaining_time().days <= 0:
                self._perform_last_fixture_notification(
                    last_team_fixture, team_league_standing
                )

    def _perform_last_fixture_notification(
        self, team_fixture: Fixture, team_standing: TeamStanding
    ) -> None:
        # telegram
        telegram_standing_message = f"{Emojis.RED_EXCLAMATION_MARK.value}Situación actual en el campeonato: \n\n{str(team_standing)}\n"
        for recipient in TELEGRAM_RECIPIENTS:
            telegram_message = (
                f"{Emojis.WAVING_HAND.value}Hola {recipient}!\n\n{self._get_last_match_team_intro()} "
                f"jugó ayer! Este fué el resultado: \n\n{team_fixture.matched_played_str()}\n\n{telegram_standing_message}"
            )
            send_telegram_message(
                TELEGRAM_RECIPIENTS[recipient], telegram_message, get_image_search(f"{team_fixture.home_team.name} vs {team_fixture.away_team.name}")
            )

        # email
        email_standing_message = f"{Emojis.RED_EXCLAMATION_MARK.value}Situación actual en el campeonato: \n\n{team_standing.email_like_repr()}\n"
        for recipient in EMAIL_RECIPIENTS:
            message = (
                f"{Emojis.WAVING_HAND.value}Hola {recipient}!\n\n{self._get_last_match_team_intro()} "
                f"jugó ayer! Este fue el resultado: \n\n{team_fixture.matched_played_email_like_repr()}"
                f"<br /><br />{email_standing_message}"
            )

            send_email_html(
                f"{team_fixture.home_team.name} ({team_fixture.match_score.home_score}) - "
                f"({team_fixture.match_score.away_score}) {team_fixture.away_team.name}",
                message,
                EMAIL_RECIPIENTS[recipient],
            )

    def _perform_fixture_notification(self, team_fixture: Fixture) -> None:
        spanish_format_date = get_date_spanish_text_format(team_fixture.bsas_date)

        date_text = (
            "es HOY!"
            if team_fixture.utc_date.day == datetime.today().day
            else f"es el {Emojis.SPIRAL_CALENDAR.value} {spanish_format_date}."
        )

        # whatsapp
        for recipient in RECIPIENTS:
            message = f"{Emojis.WAVING_HAND.value}Hola {recipient}!\n\n{self._get_team_intro()} {date_text}\n\n{str(team_fixture)}"
            send_whatsapp_message(RECIPIENTS[recipient], message)

        # telegram
        for recipient in TELEGRAM_RECIPIENTS:
            telegram_message = f"{Emojis.WAVING_HAND.value}Hola {recipient}!\n\n{self._get_team_intro(True)} {date_text}\n\n{str(team_fixture)}"
            send_telegram_message(
                TELEGRAM_RECIPIENTS[recipient], telegram_message, self._team_logo
            )

        # email
        for recipient in EMAIL_RECIPIENTS:
            message = f"{Emojis.WAVING_HAND.value}Hola {recipient}!\n\n{self._get_team_intro()} {date_text}\n\n{team_fixture.email_like_repr()}"

            send_email_html(
                f"{team_fixture.home_team.name} vs. {team_fixture.away_team.name}",
                message,
                EMAIL_RECIPIENTS[recipient],
            )

    def _get_last_match_team_intro(self) -> str:
        if self._team_id == "85":
            return f"El PSG {Emojis.FRANCE.value} de Lionel Messi {Emojis.GOAT.value}"
        elif self._team_id == "435":
            return f"El River de Marcelo Gallardios"
        elif self._team_id == "26":
            return f"La Scaloneta {Emojis.ARGENTINA.value}"
        else:
            return ""

    def _get_team_intro(self, is_group_notification: bool = False) -> str:
        pronoun = "Les" if is_group_notification else "Te"
        if self._team_id == "85":
            return (
                f"{pronoun} recuerdo que el próximo partido del PSG {Emojis.FRANCE.value}"
                f" de Lionel Messi {Emojis.GOAT.value}"
            )
        elif self._team_id == "435":
            return f"{pronoun} recuerdo que el próximo partido del River de Marcelo Gallardios"
        elif self._team_id == "26":
            return f"{pronoun} recuerdo que el próximo partido de La Scaloneta {Emojis.ARGENTINA.value}"
        else:
            return ""
