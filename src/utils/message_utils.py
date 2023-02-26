from typing import List

from src.emojis import Emojis
from src.entities import Fixture, Team
from src.notifier_constants import TELEGRAM_MSG_LENGTH_LIMIT
from src.notifier_logger import get_logger

TEAMS_ALIASES = {"85": ["PSG"]}

logger = get_logger(__name__)


def get_first_phrase_msg(
    is_group_notification: bool = False, is_on_demand: bool = False
) -> str:
    pronoun = "Les" if is_group_notification else "Te"
    first_phrase = (
        f"{pronoun} recuerdo que el próximo partido"
        if not is_on_demand
        else "El próximo partido"
    )

    return first_phrase


def get_team_intro_message(team: Team):
    switch = {
        "85": {
            "next_match": f"del PSG {Emojis.FRANCE.value}"
            f" de Lionel Messi {Emojis.GOAT.value}",
            "last_match": f"El PSG {Emojis.FRANCE.value} de Lionel Messi {Emojis.GOAT.value}",
        },
        "435": {
            "next_match": f"del River de Marcelo Gallardios {Emojis.WHITE_CIRCLE.value}{Emojis.RED_CIRCLE.value}",
            "last_match": f"El River {Emojis.WHITE_CIRCLE.value}{Emojis.RED_CIRCLE.value} de Marcelo Gallardios",
        },
        "26": {
            "next_match": f"de La Scaloneta {Emojis.ARGENTINA.value}",
            "last_match": f"La Scaloneta {Emojis.ARGENTINA.value}",
        },
        "451": {
            "next_match": f"de La Battaglieta {Emojis.BLUE_CIRCLE.value}{Emojis.YELLOW_CIRCLE.value}",
            "last_match": f"La Battaglieta {Emojis.BLUE_CIRCLE.value}{Emojis.YELLOW_CIRCLE.value}",
        },
        "440": {
            "next_match": f"de Belgrano {Emojis.PIRATE_FLAG.value}",
            "last_match": f"Belgrano {Emojis.PIRATE_FLAG.value}",
        },
    }

    default_team_msgs = {
        "next_match": f"de {team.name}",
        "last_match": team.name,
    }

    return switch.get(team.id, default_team_msgs)


def get_highlights_text(highlights: List[str], email: bool = False) -> str:
    endline = "<br />" if email else "\n"
    highlights_text = ""
    highlight_number = 1

    for highlight in highlights:
        highlights_text += f"{Emojis.FILM_PROJECTOR.value} <a href='{highlight}'>HIGHLIGHTS [{highlight_number}]</a>{endline}"
        highlight_number += 1

    return highlights_text


def get_list_of_fitting_texts(
    list_of_texts: List[str], separator: str = f"\n"
) -> List[List[str]]:
    fitting_texts = []
    current_fitting_texts = []
    current_text = ""

    for text in list_of_texts:
        if len(f"{current_text}{separator}{text}") > TELEGRAM_MSG_LENGTH_LIMIT:
            fitting_texts.append(current_fitting_texts)
            current_text = ""
            current_fitting_texts = []
        else:
            current_text += f"{separator}{text}"
            current_fitting_texts.append(text)

    if current_fitting_texts:
        fitting_texts.append(current_fitting_texts)

    return [f"{separator}".join(texts) for texts in fitting_texts]


@staticmethod
def get_fixtures_text(
    converted_fixtures: List[Fixture], played: bool = False, with_date: bool = False
) -> List[str]:
    fixtures_text = ""
    all_fitting_fixtures = []
    current_fitting_fixtures = []

    for fixture in converted_fixtures:
        fixture_text = fixture.one_line_telegram_repr(played, with_date)

        if len(f"{fixtures_text}\n\n{fixture_text}") > TELEGRAM_MSG_LENGTH_LIMIT:
            all_fitting_fixtures.append(current_fitting_fixtures)
            fixtures_text = ""
            current_fitting_fixtures = []
        else:
            fixtures_text += "\n\n" + fixture_text
            current_fitting_fixtures.append(fixture)

    if current_fitting_fixtures:
        all_fitting_fixtures.append(current_fitting_fixtures)

    logger.info(f"All fitting fixtures: {all_fitting_fixtures}")

    return [
        "\n\n".join(
            [
                fitting_fixture.one_line_telegram_repr(played, with_date)
                for fitting_fixture in fitting_fixtures
            ]
        )
        for fitting_fixtures in all_fitting_fixtures
    ]
