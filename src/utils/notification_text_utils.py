import random
from datetime import datetime
from typing import List

from src.db.fixtures_db_manager import FixturesDBManager
from src.emojis import Emojis
from src.entities import Fixture

FIXTURES_DB_MANAGER = FixturesDBManager()


def telegram_last_team_or_league_fixture_notification(
    team_fixture: Fixture, team_or_league: str, user: str = ""
) -> tuple:
    match_images = _get_match_images(team_fixture)
    match_image_url = random.choice(match_images)

    match_date = (
        "TODAY!"
        if team_fixture.bsas_date.date() == datetime.today().date()
        else f"on {Emojis.SPIRAL_CALENDAR.value} {team_fixture.bsas_date.strftime('%A')[:3]}. {team_fixture.bsas_date.strftime('%d-%m-%Y')}\n"
    )

    if (
        "first" in team_fixture.match_status.lower()
        or "half" in team_fixture.match_status.lower()
        or "second" in team_fixture.match_status.lower()
    ):
        match_text_content = f"The last match of {team_or_league} is being played! \n\n"
    else:
        match_text_content = f"The last match of {team_or_league} was {match_date} \n\n"

    telegram_message = (
        f"{Emojis.WAVING_HAND.value}Hi {user}!\n\n"
        f"{match_text_content}"
        f"{team_fixture.matched_played_telegram_like_repr()}"
        f"{Emojis.FILM_PROJECTOR.value} {team_fixture.get_html_highlights_text()}"
    )

    return (telegram_message, match_image_url)


def telegram_next_team_or_league_fixture_notification(
    team_fixture: Fixture, team_or_league: str, user: str = ""
) -> tuple:
    match_images = _get_match_images(team_fixture)
    match_image_url = random.choice(match_images)

    match_date = (
        "TODAY!"
        if team_fixture.bsas_date.date() == datetime.today().date()
        else f"on {Emojis.SPIRAL_CALENDAR.value} {team_fixture.bsas_date.strftime('%A')[:3]}. {team_fixture.bsas_date.strftime('%d-%m-%Y')}\n"
    )

    telegram_message = (
        f"{Emojis.WAVING_HAND.value}Hi {user}! "
        f"\n\nThe next match of {team_or_league} is {match_date}\n\n"
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
