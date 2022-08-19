from typing import Optional

from config.whatsapp_notif import RECIPIENTS
from src.api.players_client import PlayersClient
from src.senders.whatsapp_sender import send_whatsapp_message
from src.utils.players_utils import get_all_player_stats


class PlayerStatisticsManager:
    def __init__(
        self, season: int, player_id: int, team_filter: Optional[str] = ""
    ) -> None:
        self._season = season
        self._player_id = player_id
        self._team_filter = team_filter
        self._players_client = PlayersClient()

    def notify_player_statistics(self) -> None:
        player_stats = self._players_client.get_players_stats_by(
            self._season, self._player_id
        )

        player_stats_response = player_stats.as_dict["response"][0]

        all_player_stats = get_all_player_stats(
            player_stats_response, self._team_filter
        )

        for recipient in RECIPIENTS:
            message = f"Hola {recipient}!\nEstas son las estatidiscas actualizadas de Lionel Messi:\n\n{str(all_player_stats)}"
            send_whatsapp_message(RECIPIENTS[recipient], message)
