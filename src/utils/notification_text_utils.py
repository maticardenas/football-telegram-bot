import random
from datetime import datetime
from typing import List

from src.db.fixtures_db_manager import FixturesDBManager
from src.emojis import Emojis
from src.entities import Fixture
from src.utils.date_utils import get_date_spanish_text_format

FIXTURES_DB_MANAGER = FixturesDBManager()


def telegram_last_fixture_team_notification(
    team_fixture: Fixture, team: str, user: str = ""
) -> tuple:
    match_images = _get_match_images(team_fixture)
    match_image_url = random.choice(match_images)
    spanish_format_date = get_date_spanish_text_format(team_fixture.bsas_date)

    highlights_yt_url = (
        f"https://www.youtube.com/results?search_query="
        f"{team_fixture.home_team.name}+vs+{team_fixture.away_team.name}+jugadas+resumen"
    )

    highlights_text = (
        f"{Emojis.FILM_PROJECTOR.value} <a href='{highlights_yt_url}'>HIGHLIGHTS</a>"
    )

    match_date = (
        "HOY!"
        if team_fixture.bsas_date.date() == datetime.today().date()
        else f"el {spanish_format_date}"
    )

    telegram_message = (
        f"{Emojis.WAVING_HAND.value}Hi {user}!\n\n"
        f"{team} jugó {match_date} \n\n"
        f"{team_fixture.matched_played_telegram_like_repr()}"
        f"{highlights_text}"
    )

    return (telegram_message, match_image_url)


def telegram_last_fixture_league_notification(
    team_fixture: Fixture, league: str, user: str = ""
) -> tuple:
    match_images = _get_match_images(team_fixture)
    match_image_url = random.choice(match_images)
    spanish_format_date = get_date_spanish_text_format(team_fixture.bsas_date)

    highlights_yt_url = (
        f"https://www.youtube.com/results?search_query="
        f"{team_fixture.home_team.name}+vs+{team_fixture.away_team.name}+jugadas+resumen"
    )

    highlights_text = (
        f"{Emojis.FILM_PROJECTOR.value} <a href='{highlights_yt_url}'>HIGHLIGHTS</a>"
    )

    match_date = (
        "TODAY!"
        if team_fixture.bsas_date.date() == datetime.today().date()
        else f"el {spanish_format_date}"
    )

    telegram_message = (
        f"{Emojis.WAVING_HAND.value}Hi {user}!\n\n"
        f"The last game of {league} was {match_date} \n\n"
        f"{team_fixture.matched_played_telegram_like_repr()}"
        f"{highlights_text}"
    )

    return (telegram_message, match_image_url)


def telegram_next_team_fixture_notification(
    team_fixture: Fixture, team: str, user: str = ""
) -> tuple:
    spanish_format_date = get_date_spanish_text_format(team_fixture.bsas_date)
    match_images = _get_match_images(team_fixture)
    match_image_url = random.choice(match_images)

    match_date = (
        "HOY!"
        if team_fixture.bsas_date.date() == datetime.today().date()
        else f"el {spanish_format_date}"
    )

    telegram_message = (
        f"{Emojis.WAVING_HAND.value}Hi {user}! "
        f"\n\nEl próximo partido de {team} es {match_date}\n\n"
        f"{team_fixture.telegram_like_repr()}"
    )

    return (telegram_message, match_image_url)


def telegram_next_league_fixture_notification(
    team_fixture: Fixture, league: str, user: str = ""
) -> tuple:
    spanish_format_date = get_date_spanish_text_format(team_fixture.bsas_date)
    match_images = _get_match_images(team_fixture)
    match_image_url = random.choice(match_images)

    match_date = (
        "HOY!"
        if team_fixture.bsas_date.date() == datetime.today().date()
        else f"el {spanish_format_date}"
    )

    telegram_message = (
        f"{Emojis.WAVING_HAND.value}Hi {user}! "
        f"\n\nEl próximo partido de {league} es {match_date}\n\n"
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
