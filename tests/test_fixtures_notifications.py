from src.entities import Fixture
from src.utils.notification_text_utils import telegram_last_fixture_team_notification



def test_telegram_last_fixture_team_notification(fixture: Fixture):
    # given - when - then
    print(telegram_last_fixture_team_notification(fixture, "River Plate"))