import os
from datetime import datetime
import pytz
from freezegun import freeze_time

from src.entities import FixtureForDB
from src.utils.date_utils import get_date_spanish_text_format
from src.utils.fixtures_utils import (
    date_diff,
    get_next_fixture,
    convert_fixtures_response_to_db,
)
from tests.utils.sample_data_utils import get_sample_data_response

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(TESTS_DIR, "data")


def test_get_next_fixture():
    # given
    fixture_response_json_file = "fixtures_response_sample.json"
    fixture_response = get_sample_data_response(DATA_PATH, fixture_response_json_file)

    # when
    with freeze_time("2021-09-29 18:30:00"):
        next_fixture = get_next_fixture(fixture_response, "435")

    # then
    assert next_fixture.utc_date == datetime.strptime(
        f"2021-09-29T18:45:00+00:00"[:-6], "%Y-%m-%dT%H:%M:%S"
    )
    assert next_fixture.home_team.name == "Peterborough"
    assert next_fixture.away_team.name == "Bournemouth"
    assert next_fixture.championship.name == "Championship"
    assert next_fixture.match_status == "Not Started"
    assert next_fixture.referee == "A.  Woolmer"
    assert next_fixture.round == "Regular Season - 10"


def test_date_diff():
    # given
    date = "2021-09-30T18:45:00+00:00"

    # when
    with freeze_time("2021-09-28 18:30:00"):
        dates_diff = date_diff(date)

    # then
    assert dates_diff.days == 2


def test_date_conversion():
    # given
    date = "2021-09-29T18:45:00+00:00"
    utc_date = datetime.strptime(date[:-6], "%Y-%m-%dT%H:%M:%S")

    # when
    amsterdam_tz = pytz.timezone("Europe/Amsterdam")
    bsas_tz = pytz.timezone("America/Argentina/Buenos_Aires")

    local_dt = utc_date.replace(tzinfo=pytz.utc).astimezone(amsterdam_tz)
    bsas_dt = utc_date.replace(tzinfo=pytz.utc).astimezone(bsas_tz)

    local_definitive_date = amsterdam_tz.normalize(local_dt)
    bsas_definitive_date = bsas_tz.normalize(bsas_dt)

    # then
    assert local_definitive_date
    assert bsas_definitive_date


def test_get_date_spanish_text_format():
    # given
    date = datetime.strptime("2021-10-29T18:45:00", "%Y-%m-%dT%H:%M:%S")

    # when
    formatted_date = get_date_spanish_text_format(date)

    # then
    assert formatted_date == "Viernes 29 de Octubre del 2021"


def test_convert_fixtures_response_to_db():
    # given
    fixture_response_json_file = "fixtures_response_sample.json"
    fixture_response = get_sample_data_response(DATA_PATH, fixture_response_json_file)

    # when
    converted_fixtures = convert_fixtures_response_to_db(fixture_response)

    # then
    assert len(converted_fixtures) == 54
    assert all([isinstance(fixture, FixtureForDB) for fixture in converted_fixtures])
