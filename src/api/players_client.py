from typing import Any, Dict

import httpx

from src.api.base_client import BaseClient


class PlayersClient(BaseClient):
    def __init__(self) -> None:
        super().__init__()
        self.endpoint = "/v3/players"

    def get_players_stats_by(self, season: int, player_id: int) -> Dict[str, Any]:
        params = {"season": season, "id": player_id}
        url = f"{self.base_url}{self.endpoint}"

        return httpx.get(url, params, self.headers)
