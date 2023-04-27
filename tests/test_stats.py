import pytest

from src.emojis import Emojis
from src.statistics.team_stats import TeamRecord


@pytest.mark.parametrize(
    "games_won, games_drawn, games_lost, expected_emoji",
    [
        (5, 0, 5, Emojis.FACE_WITHOUT_MOUTH),
        (5, 2, 2, Emojis.SMILEY_FACE),
        (5, 8, 4, Emojis.FACE_WITHOUT_MOUTH),
        (2, 2, 4, Emojis.SAD_FACE),
        (3, 1, 5, Emojis.SAD_FACE),
    ],
)
def test_team_record(
    games_won: int, games_drawn: int, games_lost: int, expected_emoji: Emojis
):
    team_record = TeamRecord(
        games_won=games_won, games_drawn=games_drawn, games_lost=games_lost
    )

    assert team_record.emoji == expected_emoji.value
