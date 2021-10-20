from datetime import datetime

from config.email_notif import EMAIL_RECIPIENTS
from config.telegram_notif import TELEGRAM_RECIPIENTS
from config.whatsapp_notif import RECIPIENTS
from src.api.fixtures_client import FixturesClient
from src.emojis import Emojis
from src.entities import Fixture
from src.senders.email_sender import send_email_html
from src.senders.telegram_sender import send_telegram_message
from src.utils.date_utils import get_date_spanish_text_format
from src.utils.fixtures_utils import get_next_fixture
from src.senders.whatsapp_sender import send_whatsapp_message


class TeamFixturesManager:
    def __init__(self, season: str, team_id: str) -> None:
        self._season = season
        self._team_id = team_id
        self._fixtures_client = FixturesClient()

    def notify_next_fixture(self) -> None:
        team_fixtures = self._fixtures_client.get_fixtures_by(self._season, self._team_id)

        next_team_fixture = get_next_fixture(team_fixtures.as_dict["response"])

        if next_team_fixture:
            if next_team_fixture.remaining_time().days < 3:
                self._perform_fixture_notification(next_team_fixture)

    def _perform_fixture_notification(self, team_fixture: Fixture) -> None:
        spanish_format_date = get_date_spanish_text_format(team_fixture.bsas_date)

        date_text = f"es el {Emojis.SPIRAL_CALENDAR.value} {spanish_format_date}" \
                    if team_fixture.remaining_time().days > 0 else "es HOY!"

        # whatsapp
        for recipient in RECIPIENTS:
            message = f"{Emojis.WAVING_HAND.value}Hola {recipient}!\n\n{self._get_team_intro()} {date_text}.\n\n{str(team_fixture)}"
            send_whatsapp_message(RECIPIENTS[recipient], message)

        # telegram
        for recipient in TELEGRAM_RECIPIENTS:
            telegram_message = f"{Emojis.WAVING_HAND.value}Hola {recipient}!\n\n{self._get_team_intro(True)} {date_text}.\n\n{str(team_fixture)}"
            send_telegram_message(TELEGRAM_RECIPIENTS[recipient], telegram_message)

        # email
        for recipient in EMAIL_RECIPIENTS:
            message = f"{Emojis.WAVING_HAND.value}Hola {recipient}!\n\n{self._get_team_intro()} {date_text}.\n\n{team_fixture.email_like_repr()}"

            send_email_html(f"{team_fixture.home_team} vs. {team_fixture.away_team}", message, EMAIL_RECIPIENTS[recipient])

    def _get_team_intro(self, is_group_notification: bool = False) -> str:
        pronoun = "Les" if is_group_notification else "Te"
        if self._team_id == "85":
            return f"{pronoun} recuerdo que el próximo partido del PSG {Emojis.FRANCE.value}" \
                    f" de Lionel Messi {Emojis.GOAT.value}"
        elif self._team_id == "435":
            return f"{pronoun} recuerdo que el próximo partido del River de Marcelo Gallardios"
        elif self._team_id == "26":
            return f"{pronoun} recuerdo que el próximo partido de La Scaloneta"
        else:
            return ""