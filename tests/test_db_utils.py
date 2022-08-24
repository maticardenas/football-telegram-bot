import copy

from src.db.notif_sql_models import Fixture
from src.utils.db_utils import remove_duplicate_fixtures


def test_remove_duplicate_fixtures(fixture: Fixture):
    # given
    repeated_fixture = copy.deepcopy(fixture)
    all_fixtures = [fixture, repeated_fixture]

    # when
    fixtures = remove_duplicate_fixtures(all_fixtures)

    # then
    assert len(fixtures) == 1


def test_remove_duplicate_fixtures_no_duplicates(fixture: Fixture):
    # given
    other_fixture = copy.deepcopy(fixture)
    other_fixture.id = 123
    all_fixtures = [fixture, other_fixture]

    # when
    fixtures = remove_duplicate_fixtures(all_fixtures)

    # then
    assert len(fixtures) == 2


def test_remove_multiple_duplicate_fixtures(fixture: Fixture):
    # given
    repeated_fixture_1 = copy.deepcopy(fixture)
    repeated_fixture_1.id = 111
    repeated_fixture_2 = copy.deepcopy(fixture)
    repeated_fixture_2.id = 111
    repeated_fixture_3 = copy.deepcopy(fixture)
    repeated_fixture_3.id = 123
    repeated_fixture_4 = copy.deepcopy(fixture)
    repeated_fixture_4.id = 123
    all_fixtures = [
        fixture,
        repeated_fixture_1,
        repeated_fixture_2,
        repeated_fixture_3,
        repeated_fixture_4,
    ]

    # when
    fixtures = remove_duplicate_fixtures(all_fixtures)

    # then
    assert len(fixtures) == 3
