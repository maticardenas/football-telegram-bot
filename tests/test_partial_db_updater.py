from pathlib import Path

from dotenv import load_dotenv

from partial_db_updater import get_fixture_update_lots

current_path = Path(__file__).parent.absolute()
env_file = current_path / ".." / "football_notifier.env"
load_dotenv(env_file)


def test_get_fixture_update_lots():
    # given
    all_fixtures_ids = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
    ]

    # when
    fixture_lots = get_fixture_update_lots(all_fixtures_ids)

    # then
    fixture_lots_list = list(fixture_lots)
    assert fixture_lots_list == [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    ]
