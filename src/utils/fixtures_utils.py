import re
import urllib
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.error import HTTPError

from deep_translator import GoogleTranslator
from sqlmodel import select

from src.api.fixtures_client import FixturesClient
from src.api.images_search_client import ImagesSearchClient
from src.api.videos_search_client import VideosSearchClient
from src.api.youtube_search_client import YoutubeSearchClient
from src.converters.converters import LineUpConverter
from src.db.db_manager import NotifierDBManager
from src.db.fixtures_db_manager import FixturesDBManager
from src.db.line_ups_db_manager import LineUpsDBManager
from src.db.notif_sql_models import Event as DBEvent
from src.db.notif_sql_models import Fixture as DBFixture
from src.db.notif_sql_models import League as DBLeague
from src.db.notif_sql_models import Team as DBTeam
from src.db.notif_sql_models import UserTimeZone
from src.entities import (
    Assist,
    Championship,
    Event,
    Fixture,
    FixtureForDB,
    LineUp,
    MatchHighlights,
    MatchScore,
    Player,
    Team,
    TeamStanding,
    Time,
)
from src.notifier_logger import get_logger
from src.utils.date_utils import TimeZones, get_time_in_time_zone

FIXTURES_DB_MANAGER = FixturesDBManager()
LINE_UPS_DB_MANAGER = LineUpsDBManager()
FIXTURES_CLIENT = FixturesClient()

logger = get_logger(__name__)


def date_diff(date: str) -> datetime:
    return datetime.strptime(date[:-6], "%Y-%m-%dT%H:%M:%S") - datetime.utcnow()


def get_next_fixture(
    team_fixtures: List[Dict[str, Any]], team_id: str
) -> Optional[Fixture]:
    min_fixture = None
    min_diff = 999999999

    for fixture in team_fixtures:
        fixture_date_diff = int(date_diff(fixture["fixture"]["date"]).total_seconds())

        if not min_fixture and fixture_date_diff >= 0:
            min_fixture = fixture
            min_diff = fixture_date_diff

        if fixture_date_diff >= 0 and (fixture_date_diff < min_diff):
            min_fixture = fixture
            min_diff = fixture_date_diff

    return (
        convert_fixture_response(min_fixture, min_diff, team_id)
        if min_fixture
        else None
    )


def get_next_fixture_db(team_fixtures: List[DBFixture]) -> Optional[DBFixture]:
    min_fixture = None
    min_diff = 999999999

    for fixture in team_fixtures:
        fixture_date_diff = int(date_diff(fixture.utc_date).total_seconds())

        if not min_fixture and fixture_date_diff >= 0:
            min_fixture = fixture
            min_diff = fixture_date_diff

        if fixture_date_diff >= 0 and (fixture_date_diff < min_diff):
            min_fixture = fixture
            min_diff = fixture_date_diff

    converted_fixture = None

    if min_fixture:
        converted_fixture = convert_db_fixture(min_fixture)
        converted_fixture.head_to_head = get_head_to_heads(
            converted_fixture.home_team.id, converted_fixture.away_team.id
        )

    return converted_fixture


def get_last_fixture_db(team_fixtures: List[DBFixture]) -> Optional[Fixture]:
    min_fixture = None
    min_diff = -999999999

    for fixture in team_fixtures:
        fixture_date_diff = int(date_diff(fixture.utc_date).total_seconds())

        if not min_fixture and fixture_date_diff < 0:
            min_fixture = fixture
            min_diff = fixture_date_diff

        if fixture_date_diff < 0 and (fixture_date_diff > min_diff):
            min_fixture = fixture
            min_diff = fixture_date_diff

    converted_fixture = None

    if min_fixture:
        converted_fixture = convert_db_fixture(min_fixture)
        converted_fixture.head_to_head = get_head_to_heads(
            converted_fixture.home_team.id, converted_fixture.away_team.id
        )

    return converted_fixture


def is_today_fixture(team_fixture: DBFixture) -> bool:
    utc_date = datetime.strptime(team_fixture.utc_date[:-6], "%Y-%m-%dT%H:%M:%S")
    bsas_date = get_time_in_time_zone(utc_date, TimeZones.BSAS)

    return bsas_date.date() == datetime.today().date()


def insert_head_to_heads() -> Optional[List[Fixture]]:
    tomorrow_games = FIXTURES_DB_MANAGER.get_games_in_surrounding_n_days(5)

    for game in tomorrow_games:
        head_to_head = FIXTURES_CLIENT.get_head_to_head(game.home_team, game.away_team)
        if "response" in head_to_head.as_dict:
            head_to_head_fixtures = head_to_head.as_dict["response"]
            if head_to_head_fixtures:
                FIXTURES_DB_MANAGER.save_fixtures(
                    [
                        convert_fixture_response_to_db_fixture(fixture)
                        for fixture in head_to_head_fixtures
                    ]
                )


def convert_fixtures_response_to_db(
    fixtures_response: Union[List[dict], List[List[dict]]]
) -> List[DBFixture]:
    """
    :param fixtures_response: "response" key from fixtures response. It can be either a list of individual fixtures
    or a list of lists (max 100) if response includes too many fixtures.

    :return: a list of converted fixtures to DB entities.
    """
    converted_db_fixtures = []

    for item in fixtures_response:
        if isinstance(item, list):
            for fixture in item:
                converted_db_fixtures.append(
                    convert_fixture_response_to_db_fixture(fixture)
                )
        else:
            converted_db_fixtures.append(convert_fixture_response_to_db_fixture(item))

    return converted_db_fixtures


def get_head_to_heads(team_1: str, team_2: str) -> Optional[List[Fixture]]:
    head_to_head_fixtures = FIXTURES_DB_MANAGER.get_head_to_head_fixtures(
        team_1, team_2
    )
    return [convert_db_fixture(fixture) for fixture in head_to_head_fixtures]


def get_last_fixture(
    team_fixtures: List[Dict[str, Any]], team_id: str
) -> Optional[Fixture]:
    min_fixture = None
    min_diff = -999999999

    for fixture in team_fixtures:
        fixture_date_diff = int(date_diff(fixture["fixture"]["date"]).total_seconds())

        if not min_fixture and fixture_date_diff < 0:
            min_fixture = fixture
            min_diff = fixture_date_diff

        if fixture_date_diff < 0 and (fixture_date_diff > min_diff):
            min_fixture = fixture
            min_diff = fixture_date_diff

    return (
        convert_fixture_response(min_fixture, min_diff, team_id)
        if min_fixture
        else None
    )


def convert_db_event(event: DBEvent, rival_team: Optional[DBTeam] = None) -> Event:
    event_db_player = FIXTURES_DB_MANAGER.get_player(event.player)
    event_db_assist = FIXTURES_DB_MANAGER.get_player(event.assist)
    event_db_team = FIXTURES_DB_MANAGER.get_team(event.team)

    return Event(
        time=Time(
            elapsed=event.time,
            extra=event.time_extra,
        ),
        team=Team(
            id=event_db_team[0].id,
            name=event_db_team[0].name,
            logo=event_db_team[0].picture,
            country=event_db_team[0].country,
            picture=event_db_team[0].picture,
        ),
        player=Player(
            id=event_db_player[0].id if len(event_db_player) else None,
            name=event_db_player[0].name if len(event_db_player) else None,
        ),
        assist=Assist(
            id=event_db_assist[0].id if len(event_db_assist) else None,
            name=event_db_assist[0].name if len(event_db_assist) else None,
        )
        if len(event_db_assist)
        else Assist(),
        type=event.type,
        detail=event.detail,
        comments=event.comments,
        fixture_id=event.fixture,
        rival_team=Team(
            id=rival_team.id,
            name=rival_team.name,
            logo=rival_team.picture,
            country=rival_team.country,
            picture=rival_team.picture,
        )
        if rival_team
        else None,
    )


def convert_db_fixture(
    fixture: DBFixture, user_time_zones: Optional[List[UserTimeZone]] = []
) -> Fixture:
    """
    Converts a fixture from database into a Fixture entity for notifying.
    """
    utc_date = datetime.strptime(fixture.utc_date[:-6], "%Y-%m-%dT%H:%M:%S")
    ams_date = get_time_in_time_zone(utc_date, TimeZones.AMSTERDAM)
    bsas_date = get_time_in_time_zone(utc_date, TimeZones.BSAS)

    # league_name, round_name = __get_translated_league_name_and_round(fixture)
    notifier_db_manager = NotifierDBManager()

    main_time_zone = FIXTURES_DB_MANAGER.get_time_zones_by_name("UTC")[0]
    additional_time_zones = []

    for user_time_zone in user_time_zones:
        db_time_zone = FIXTURES_DB_MANAGER.get_time_zone(user_time_zone.time_zone)[0]
        if user_time_zone.is_main_tz is True:
            main_time_zone = db_time_zone
        else:
            additional_time_zones.append(db_time_zone)

    league: DBLeague = notifier_db_manager.select_records(
        select(DBLeague).where(DBLeague.id == fixture.league)
    )[0]
    home_team: DBTeam = notifier_db_manager.select_records(
        select(DBTeam).where(DBTeam.id == fixture.home_team)
    )[0]
    away_team: DBTeam = notifier_db_manager.select_records(
        select(DBTeam).where(DBTeam.id == fixture.away_team)
    )[0]
    fixture_db_events = FIXTURES_DB_MANAGER.get_fixture_events(fixture.id)
    fixture_events = (
        [
            convert_db_event(
                db_event, away_team if db_event.team == home_team.id else home_team
            )
            for db_event in fixture_db_events
        ]
        if has_all_events(fixture, fixture_db_events)
        else []
    )

    home_line_up, away_line_up = None, None
    db_line_ups = LINE_UPS_DB_MANAGER.get_fixture_line_ups(fixture_id=fixture.id)

    if len(db_line_ups):
        line_ups_converter = LineUpConverter()
        home_team_line_up = list(
            filter(lambda liup: liup.team == home_team.id, db_line_ups)
        )
        away_team_line_up = list(
            filter(lambda liup: liup.team == away_team.id, db_line_ups)
        )
        home_line_up = line_ups_converter.db_model_to_entity(
            formation=home_team_line_up[0].formation or "",
            line_up=home_team_line_up,
        )
        away_line_up = line_ups_converter.db_model_to_entity(
            formation=away_team_line_up[0].formation or "",
            line_up=away_team_line_up,
        )

    return Fixture(
        fixture.id,
        utc_date,
        ams_date,
        bsas_date,
        int(date_diff(fixture.utc_date).total_seconds()),
        fixture.referee,
        fixture.match_status,
        Championship(
            league.id,
            league.name,
            league.country,
            league.logo,
        ),
        fixture.round,
        Team(
            id=home_team.id,
            name=home_team.name,
            logo=home_team.picture,
            aliases=[],
            country=home_team.country,
        ),
        Team(
            id=away_team.id,
            name=away_team.name,
            logo=away_team.picture,
            aliases=[],
            country=away_team.country,
        ),
        MatchScore(
            fixture.home_score,
            fixture.away_score,
            fixture.penalty_home_score,
            fixture.penalty_away_score,
        ),
        fixture.venue,
        additional_time_zones=additional_time_zones,
        main_time_zone=main_time_zone,
        events=fixture_events,
        home_team_line_up=home_line_up,
        away_team_line_up=away_line_up,
    )


def get_all_events_goals(events: List[DBEvent]) -> int:
    return sum(
        1
        for event in events
        if event.type == "Goal"
        and event.detail != "Missed Penalty"
        and event.comments != "Penalty Shootout"
        and event.player is not None
    )


def has_all_events(fixture: DBFixture, events) -> bool:
    if fixture.home_score is None or fixture.away_score is None:
        return False

    all_fixture_goals = fixture.home_score + fixture.away_score

    return get_all_events_goals(events) == all_fixture_goals


def convert_fixture_response(
    fixture_response: Dict[str, Any], date_diff: int, team_id: str = 1
) -> Fixture:
    utc_date = datetime.strptime(
        fixture_response["fixture"]["date"][:-6], "%Y-%m-%dT%H:%M:%S"
    )
    ams_date = get_time_in_time_zone(utc_date, TimeZones.AMSTERDAM)
    bsas_date = get_time_in_time_zone(utc_date, TimeZones.BSAS)

    league_name, round_name = __get_translated_league_name_and_round(fixture_response)
    home_team_id = fixture_response["teams"]["home"]["id"]
    away_team_id = fixture_response["teams"]["away"]["id"]

    return Fixture(
        fixture_response["fixture"]["id"],
        utc_date,
        ams_date,
        bsas_date,
        date_diff,
        fixture_response["fixture"]["referee"],
        fixture_response["fixture"]["status"]["long"],
        Championship(
            fixture_response["league"]["id"],
            league_name,
            fixture_response["league"]["country"],
            fixture_response["league"]["logo"],
        ),
        round_name,
        Team(
            home_team_id,
            fixture_response["teams"]["home"]["name"],
            fixture_response["teams"]["home"]["logo"],
            [],
        ),
        Team(
            away_team_id,
            fixture_response["teams"]["away"]["name"],
            fixture_response["teams"]["away"]["logo"],
            [],
        ),
        MatchScore(
            fixture_response["goals"]["home"],
            fixture_response["goals"]["away"],
            fixture_response["score"]["penalty"]["home"],
            fixture_response["score"]["penalty"]["away"],
        ),
        f"{fixture_response['fixture'].get('venue').get('name')} ({fixture_response['fixture'].get('venue').get('city')})",
        []
        # get_line_up(fixture_response["fixture"]["id"], team_id),
    )


def convert_fixture_response_to_db_fixture(fixture_response: Dict[str, Any]) -> Fixture:
    fixture_teams = f"{fixture_response['teams']['home']['name']} vs {fixture_response['teams']['away']['name']}"
    logger.info(f"Converting fixture response '{fixture_teams}' to DB entity")

    league_name, round_name = __get_translated_league_name_and_round(fixture_response)
    home_team_id = fixture_response["teams"]["home"]["id"]
    away_team_id = fixture_response["teams"]["away"]["id"]

    utc_date = datetime.strptime(
        fixture_response["fixture"]["date"][:-6], "%Y-%m-%dT%H:%M:%S"
    )
    bsas_date = get_time_in_time_zone(utc_date, TimeZones.BSAS)

    return FixtureForDB(
        fixture_response["fixture"]["id"],
        fixture_response["fixture"]["date"],
        datetime.strftime(bsas_date, "%Y-%m-%dT%H:%M:%S"),
        date_diff,
        fixture_response["fixture"]["referee"],
        fixture_response["fixture"]["status"]["long"],
        Championship(
            fixture_response["league"]["id"],
            league_name,
            fixture_response["league"]["country"],
            fixture_response["league"]["logo"],
        ),
        round_name,
        Team(
            id=home_team_id,
            name=fixture_response["teams"]["home"]["name"],
            logo=fixture_response["teams"]["home"]["logo"],
            aliases=[],
            picture=fixture_response["teams"]["home"]["logo"],
        ),
        Team(
            id=away_team_id,
            name=fixture_response["teams"]["away"]["name"],
            logo=fixture_response["teams"]["away"]["logo"],
            aliases=[],
            picture=fixture_response["teams"]["away"]["logo"],
        ),
        MatchScore(
            fixture_response["goals"]["home"],
            fixture_response["goals"]["away"],
            fixture_response["score"]["penalty"]["home"],
            fixture_response["score"]["penalty"]["away"],
        ),
        fixture_response["fixture"]["venue"]["name"],
    )


def __get_translated_league_name_and_round(
    fixture_response: Dict[str, Any]
) -> Tuple[str, str]:
    if __is_team_or_league_for_spanish_translation(fixture_response):
        google_translator = GoogleTranslator(source="en", target="es")
        league_name = google_translator.translate(fixture_response["league"]["name"])
        round_name = google_translator.translate(fixture_response["league"]["round"])
    else:
        league_name = fixture_response["league"]["name"]
        round_name = fixture_response["league"]["round"]

    return (league_name, round_name)


def __is_team_or_league_for_spanish_translation(
    fixture_response: Dict[str, Any]
) -> bool:
    return fixture_response["league"][
        "country"
    ].lower() == "argentina" or __teams_contain(fixture_response, "argentina")


def get_team_standings_for_league(team_standings: dict, league_id: int) -> TeamStanding:
    for team_standing in team_standings:
        if team_standing["league"]["id"] == league_id:
            return __convert_standing_response(team_standing)


def __convert_standing_response(team_standing: dict) -> TeamStanding:
    standing_desc = team_standing["league"]["standings"][0][0]
    return TeamStanding(
        Championship(
            team_standing["league"]["id"],
            team_standing["league"]["name"],
            team_standing["league"]["country"],
            team_standing["league"]["logo"],
        ),
        standing_desc["rank"],
        standing_desc["points"],
        standing_desc["goalsDiff"],
        standing_desc["description"],
    )


def __teams_contain(fixture_response: Dict[str, Any], text: str) -> bool:
    return any(
        [
            team_name
            for team_name in [
                fixture_response["teams"]["home"]["name"],
                fixture_response["teams"]["away"]["name"],
            ]
            if text in team_name.lower()
        ]
    )


def convert_match_highlights(highlights: dict) -> MatchHighlights:
    url_match = re.search("http.*?'", highlights["embed"])
    highlights_url = highlights["embed"][url_match.span()[0] : url_match.span()[1] - 1]
    return MatchHighlights(highlights_url, highlights["embed"])


def get_youtube_highlights_videos(
    home_team: Team, away_team: Team, number_of_options=3
) -> List[str]:
    youtube_client = YoutubeSearchClient()
    response = youtube_client.search_videos_by_keywords(
        [home_team.name, away_team.name, "resumen", "jugadas"], "es", "ar"
    )

    json_response = response.as_dict

    video_highlights = []

    options_selected = 0

    try:
        for item in json_response["items"]:
            title = item["snippet"]["title"]
            home_team_words = home_team.name.lower().split(" ")
            away_team_words = away_team.name.lower().split(" ")
            if (
                any(ht_word in title.lower() for ht_word in home_team_words)
                or any(alias.lower() in title.lower() for alias in home_team.aliases)
            ) and (
                any(at_word in title.lower() for at_word in away_team_words)
                or any(alias.lower() in title.lower() for alias in away_team.aliases)
            ):
                video_highlights.append(item["url"])
                options_selected += 1

            if options_selected >= number_of_options:
                break
    except Exception as e:
        print(f"There was an issue retrieving video highlights. Error: {e}")

    return video_highlights


def get_line_up(fixture_id: str, team_id: str) -> Optional[LineUp]:
    response = FIXTURES_CLIENT.get_line_up(fixture_id, team_id)
    json_response = response.as_dict["response"]

    line_up = None

    if json_response:
        if "startXI" in json_response[0]:
            start_xi = json_response[0]["startXI"]
            line_up = LineUp(
                formation=json_response[0]["formation"],
                goalkeeper=get_players(start_xi, "G")[0],
                defenders=get_players(start_xi, "D"),
                midfielders=get_players(start_xi, "M"),
                forward_strikers=get_players(start_xi, "F"),
            )

    return line_up


def get_players(start_xi: dict, position: str) -> List[Player]:
    return [
        Player(
            player["player"]["id"], player["player"]["name"], player["player"]["pos"]
        )
        for player in start_xi
        if player["player"]["pos"] == position
    ]
