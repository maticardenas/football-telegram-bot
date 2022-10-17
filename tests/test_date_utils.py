from datetime import datetime

from freezegun import freeze_time

from src.utils.date_utils import (
    get_date_diff,
    get_formatted_date,
    is_time_between,
    is_time_in_surrounding_hours,
)


def test_get_formatted_date():
    # given
    date = "2021-03-09T00:30:00+00:00"

    # when
    formatted_date = get_formatted_date(date)

    # then
    assert type(formatted_date) is datetime
    assert str(formatted_date) == "2021-03-09 00:30:00"


def test_is_time_between():
    with freeze_time("2021-09-29 18:30:00"):
        # given
        begin_time = datetime.strptime(
            "2021-09-29 16:30:00", "%Y-%m-%d %H:%M:%S"
        ).time()
        end_time = datetime.strptime("2021-09-29 19:30:00", "%Y-%m-%d %H:%M:%S").time()

        # when - then
        assert is_time_between(datetime.utcnow().time(), begin_time, end_time) is True


def test_is_time_between_false():
    with freeze_time("2021-09-29 18:30:00"):
        # given
        begin_time = datetime.strptime(
            "2021-09-29 20:30:00", "%Y-%m-%d %H:%M:%S"
        ).time()
        end_time = datetime.strptime("2021-09-29 21:30:00", "%Y-%m-%d %H:%M:%S").time()

        # when - then
        assert is_time_between(datetime.utcnow().time(), begin_time, end_time) is False


def test_is_time_in_surrounding_hours():
    with freeze_time("2021-09-29 18:30:00"):
        # given
        check_time = datetime.strptime(
            "2021-09-29 16:30:00", "%Y-%m-%d %H:%M:%S"
        ).time()

        # when - then
        assert is_time_in_surrounding_hours(check_time, hours=3) is True


def test_is_time_in_surrounding_hours_false():
    with freeze_time("2021-09-29 18:30:00"):
        # given
        check_time = datetime.strptime(
            "2021-09-29 16:30:00", "%Y-%m-%d %H:%M:%S"
        ).time()

        # when - then
        assert is_time_in_surrounding_hours(check_time, hours=1) is False


def test_get_date_diff():
    with freeze_time("2021-09-29 18:30:00"):
        # given
        check_time = datetime.strptime("2021-09-29 16:30:00", "%Y-%m-%d %H:%M:%S")

        # when
        diff = get_date_diff(check_time)

        # then
        assert diff.days == 0
        assert diff.seconds == 7200
