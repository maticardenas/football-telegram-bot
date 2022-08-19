from datetime import datetime

import pytest

from src.entities import Fixture, RemainingTime
from src.utils.date_utils import TimeZones, get_time_in_time_zone


def test_fixture_post_init(fixture: Fixture):
    # given - when - then
    assert fixture.is_next_day == ""
    assert fixture.futbol_libre_url == "https://futbollibre.net"
    assert fixture.futbol_para_todos_url == "https://futbolparatodos.online/es/"
    assert fixture.line_up == None
    assert fixture.highlights == [
        f"https://www.youtube.com/results?search_query=River Plate+vs+Boca "
        f"Juniors+jugadas+resumen"
    ]
    assert fixture.head_to_head == []


def test_matched_played_str(fixture: Fixture):
    # given - when - then
    assert (
        fixture.matched_played_str()
        == """⚽ *River Plate - 3 vs. 0 - Boca Juniors*
🏆 *Copa de la Superliga*
📌 *Primera Fecha*"""
    )


def test_time_telegram_text(fixture: Fixture):
    # given - when - then
    assert fixture.time_telegram_text() == "🇪🇺 16:00 HS  / 🇦🇷 12:00 HS"


def test_one_line_telegram_repr_not_played(fixture: Fixture):
    # given
    fixture.match_score.home_score = None
    fixture.match_score.away_score = None

    # when - then
    assert (
        fixture.one_line_telegram_repr()
        == """⚽ River Plate vs. Boca Juniors 
🏆 Copa de la Superliga (ARG)
⏰ 🇪🇺 16:00 HS  / 🇦🇷 12:00 HS"""
    )


def test_telegram_like_repr(fixture: Fixture):
    # given - when - then
    print(fixture.telegram_like_repr())
    assert (
        fixture.telegram_like_repr()
        == """🇪🇺 <strong>16:00 HS </strong>
🇦🇷 <strong>12:00 HS</strong>

⏰  for the game.

⚽ <strong>River Plate vs. Boca Juniors</strong>
🏆 <strong>Copa de la Superliga (ARG)</strong>
🏟 <strong>Estadio Monumental</strong>
👮‍♀️ <strong>Perluigi Colina</strong>

"""
    )


def test_matched_played_telegram_like_repr_half_time(fixture: Fixture):
    # given
    fixture.match_status = "First Half"

    # - when - then
    assert (
        fixture.matched_played_telegram_like_repr()
        == """🏃‍♂️ <strong>First Half</strong>

<strong>⚽ River Plate [3] vs.  [0] Boca Juniors</strong>
🏆 <strong>Copa de la Superliga (ARG)</strong>
📌 <strong>Primera Fecha</strong>
🏟 <strong>Estadio Monumental</strong>
👮‍♀️ <strong>Perluigi Colina</strong>

"""
    )


def test_matched_played_telegram_like_repr_match_finished(fixture: Fixture):
    # given
    fixture.match_status = "Match Finished"

    # when - then
    assert (
        fixture.matched_played_telegram_like_repr()
        == """<strong>⚽ River Plate [3] vs.  [0] Boca Juniors</strong>
🏆 <strong>Copa de la Superliga (ARG)</strong>
📌 <strong>Primera Fecha</strong>
🏟 <strong>Estadio Monumental</strong>
👮‍♀️ <strong>Perluigi Colina</strong>

"""
    )


def test_matched_played_telegram_like_repr_match_finished_not_venue(fixture: Fixture):
    # given
    fixture.match_status = "Match Finished"
    fixture.venue = ""

    # when - then
    assert (
        fixture.matched_played_telegram_like_repr()
        == """<strong>⚽ River Plate [3] vs.  [0] Boca Juniors</strong>
🏆 <strong>Copa de la Superliga (ARG)</strong>
📌 <strong>Primera Fecha</strong>
👮‍♀️ <strong>Perluigi Colina</strong>

"""
    )


def test_matched_played_telegram_like_repr_match_finished_not_referee(fixture: Fixture):
    # given
    fixture.match_status = "Match Finished"
    fixture.referee = ""

    # when - then
    assert (
        fixture.matched_played_telegram_like_repr()
        == """<strong>⚽ River Plate [3] vs.  [0] Boca Juniors</strong>
🏆 <strong>Copa de la Superliga (ARG)</strong>
📌 <strong>Primera Fecha</strong>
🏟 <strong>Estadio Monumental</strong>

"""
    )


def test_is_next_day_in_europe(fixture: Fixture):
    # given - when - then
    assert fixture._is_next_day_in_europe() == False


def test_is_next_day_in_europe_true(fixture: Fixture):
    # given
    next_day_date = datetime.strptime("2019-01-02T15:00:00", "%Y-%m-%dT%H:%M:%S")
    fixture.ams_date = get_time_in_time_zone(next_day_date, TimeZones.AMSTERDAM)

    # when - then
    assert fixture._is_next_day_in_europe() == True


@pytest.mark.parametrize(
    "days, hours, minutes, expected_text",
    [
        (0, 0, 5, "5 minutes"),
        (0, 2, 0, "2 hours"),
        (0, 2, 10, "2 hours and 10 minutes"),
        (3, 0, 0, "3 days"),
        (4, 0, 3, "4 days and 3 minutes"),
        (1, 5, 0, "1 day and 5 hours"),
        (1, 7, 19, "1 day, 7 hours and 19 minutes"),
    ],
)
def test_remaining_time(days: int, hours: int, minutes: int, expected_text: str):
    # given
    remaining_time = RemainingTime(days, hours, minutes)

    # when - then
    assert str(remaining_time) == expected_text
