from datetime import datetime, timedelta
from enum import Enum
from time import time

import pytz

DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

MONTHS = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]

DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

MONTHS = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]


class TimeZones(Enum):
    AMSTERDAM = "Europe/Amsterdam"
    BSAS = "America/Argentina/Buenos_Aires"


def get_time_in_time_zone_str(utc_date: datetime, time_zone: str) -> datetime:
    required_tz = pytz.timezone(time_zone)
    required_tz_dt = utc_date.replace(tzinfo=pytz.utc).astimezone(required_tz)
    return required_tz.normalize(required_tz_dt)


def get_time_in_time_zone(utc_date: datetime, time_zone: TimeZones) -> datetime:
    required_tz = pytz.timezone(time_zone.value)
    required_tz_dt = utc_date.replace(tzinfo=pytz.utc).astimezone(required_tz)
    return required_tz.normalize(required_tz_dt)


def get_date_spanish_text_format(date: datetime) -> str:
    return (
        f"{DAYS[date.weekday()]} {date.day} de {MONTHS[date.month-1]} del {date.year}"
    )


def get_formatted_date(date: str) -> datetime:
    return datetime.strptime(date[:-6], "%Y-%m-%dT%H:%M:%S")


def get_date_diff(date: datetime) -> datetime:
    return datetime.utcnow() - date


def is_time_in_surrounding_hours(check_time: time, hours: float) -> bool:
    utc_time_now = datetime.utcnow()
    begin_time = (utc_time_now - timedelta(hours=hours)).time()
    end_time = (utc_time_now + timedelta(hours=hours)).time()

    return is_time_between(check_time, begin_time, end_time)


def is_time_between(check_time: time, begin_time: time, end_time: time):
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:
        return check_time >= begin_time or check_time <= end_time
