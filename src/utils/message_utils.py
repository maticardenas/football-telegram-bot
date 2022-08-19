from typing import List

from config.config_entities import TelegramRecipient
from src.emojis import Emojis
from src.entities import Team

TEAMS_ALIASES = {"85": ["PSG"]}


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


def is_subscripted_for_team(telegram_recipient: TelegramRecipient, team_id) -> bool:
    return team_id in telegram_recipient.team_subscriptions
