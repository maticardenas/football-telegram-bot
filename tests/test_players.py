import os

from src.utils.players_utils import convert_player_stats
from tests.utils.sample_data_utils import get_sample_data_response

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(TESTS_DIR, "data")


def test_convert_player_stats():
    # given
    player_response_json_file = "player_statistics_sample.json"
    player_response = get_sample_data_response(DATA_PATH, player_response_json_file)

    # when
    players_stats = convert_player_stats(player_response[0])

    # then
    assert "Paris Saint Germain" in players_stats
    assert "Ligue 1" in players_stats["Paris Saint Germain"]
    assert "UEFA Champions League" in players_stats["Paris Saint Germain"]
    assert "Club Friendlies" in players_stats["Paris Saint Germain"]
    assert "Barcelona" in players_stats
    assert "Club Friendlies" in players_stats["Barcelona"]
    assert "Argentina" in players_stats
    assert "Copa America" in players_stats["Argentina"]
