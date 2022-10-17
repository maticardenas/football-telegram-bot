from unittest.mock import MagicMock, patch

from src.entities import Fixture
from src.utils.notification_text_utils import (
    telegram_last_team_or_league_fixture_notification,
    telegram_next_team_or_league_fixture_notification,
)


@patch("src.utils.notification_text_utils._get_match_images")
def test_telegram_next_team_or_league_fixture_notification(
    mocked_get_match_images: MagicMock, fixture: Fixture
):
    # given
    mocked_get_match_images.return_value = ["image.jpg"]

    # when - then
    assert telegram_next_team_or_league_fixture_notification(
        fixture, "River Plate"
    ) == (
        "👋Hi ! \n\nThe next match of River Plate is on 🗓 Tue. 01-01-2019\n\n\n🇪🇺 16:00 HS\n🇦🇷 12:00 HS\n\n⏰  left for the game.\n\n⚽ <strong>River Plate vs. Boca Juniors</strong>\n🏆 <strong>Copa de la Superliga (ARG)</strong>\n🏟 <strong>Estadio Monumental</strong>\n👮\u200d♀️ <strong>Perluigi Colina</strong>\n\n",
        "image.jpg",
    )


@patch("src.utils.notification_text_utils._get_match_images")
def test_telegram_last_team_or_league_fixture_notification(
    mocked_get_match_images: MagicMock, fixture: Fixture
):
    # given
    mocked_get_match_images.return_value = ["image.jpg"]

    # when - then
    assert telegram_last_team_or_league_fixture_notification(
        fixture, "River Plate"
    ) == (
        "👋Hi !\n\nThe last match of River Plate was on 🗓 Tue. 01-01-2019\n \n\n😢 <strong>Started</strong>\n\n<strong>⚽ River Plate vs. Boca Juniors</strong>\n🏆 <strong>Copa de la Superliga (ARG)</strong>\n📌 <strong>Primera Fecha</strong>\n🏟 <strong>Estadio Monumental</strong>\n👮\u200d♀️ <strong>Perluigi Colina</strong>\n\n",
        "image.jpg",
    )
