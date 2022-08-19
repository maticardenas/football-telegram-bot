from datetime import datetime
from enum import Enum

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
# DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]


class TimeZones(Enum):
    AMSTERDAM = "Europe/Amsterdam"
    BSAS = "America/Argentina/Buenos_Aires"


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
