import random
from datetime import datetime
from typing import List

from src.db.fixtures_db_manager import FixturesDBManager
from src.emojis import Emojis
from src.entities import Fixture
from src.utils.date_utils import get_time_in_time_zone_str

FIXTURES_DB_MANAGER = FixturesDBManager()


def telegram_last_team_or_league_fixture_notification(
    team_fixture: Fixture, team_or_league: str, user: str = "", time_zone: str = ""
) -> tuple:
    match_images = _get_match_images(team_fixture)
    match_image_url = random.choice(match_images)

    utc_now = datetime.utcnow()
    today_in_time_zone = (
        get_time_in_time_zone_str(utc_now, time_zone).date()
        if time_zone
        else utc_now.date()
    )
    fixture_date_in_time_zone = (
        get_time_in_time_zone_str(team_fixture.utc_date, time_zone).date()
        if time_zone
        else team_fixture.utc_date.date()
    )
    match_date = (
        "TODAY!"
        if today_in_time_zone == fixture_date_in_time_zone
        else f"on {Emojis.SPIRAL_CALENDAR.value} {fixture_date_in_time_zone.strftime('%A').title()} "
        f"{fixture_date_in_time_zone.strftime('%d-%m-%Y')}<not_translate>\n</not_translate>"
    )

    if (
        "first" in team_fixture.match_status.lower()
        or "half" in team_fixture.match_status.lower()
        or "second" in team_fixture.match_status.lower()
    ):
        match_text_content = f"The last match of {team_or_league} is being played!<not_translate> \n</not_translate>"
    else:
        match_text_content = f"The last match of {team_or_league} was {match_date}<not_translate> \n</not_translate>"

    telegram_message = (
        f"{Emojis.WAVING_HAND.value}Hi {user}!\n\n"
        f"{match_text_content}"
        f"{team_fixture.matched_played_telegram_like_repr()}"
    )

    return (telegram_message, match_image_url)


def telegram_next_team_or_league_fixture_notification(
    team_fixture: Fixture, team_or_league: str, user: str = "", time_zone: str = ""
) -> tuple:
    match_images = _get_match_images(team_fixture)
    match_image_url = random.choice(match_images)

    utc_now = datetime.utcnow()
    today_in_time_zone = (
        get_time_in_time_zone_str(utc_now, time_zone).date()
        if time_zone
        else utc_now.date()
    )
    fixture_date_in_time_zone = (
        get_time_in_time_zone_str(team_fixture.utc_date, time_zone).date()
        if time_zone
        else team_fixture.utc_date.date()
    )

    match_date = (
        "TODAY!"
        if today_in_time_zone == fixture_date_in_time_zone
        else f"on {Emojis.SPIRAL_CALENDAR.value} {fixture_date_in_time_zone.strftime('%A').title()}. {fixture_date_in_time_zone.strftime('%d-%m-%Y')}<not_translate>\n</not_translate>"
    )

    telegram_message = (
        f"{Emojis.WAVING_HAND.value}Hi {user}! "
        f"\n\nThe next match of {team_or_league} is {match_date}<not_translate>\n\n</not_translate>"
        f"{team_fixture.telegram_like_repr()}"
    )

    return (telegram_message, match_image_url)


def _get_match_images(fixture: Fixture) -> List[str]:
    home_team_image_url = FIXTURES_DB_MANAGER.get_team(fixture.home_team.id)[0].picture
    away_team_image_url = FIXTURES_DB_MANAGER.get_team(fixture.away_team.id)[0].picture
    league_image_url = FIXTURES_DB_MANAGER.get_league(fixture.championship.league_id)[
        0
    ].logo

    return [home_team_image_url, away_team_image_url, league_image_url]
