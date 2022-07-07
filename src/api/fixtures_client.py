from typing import Any, Dict, List, Tuple

from src.api.base_client import BaseClient
from src.notifier_logger import get_logger
from src.request import APIRequest

logger = get_logger(__name__)


class FixturesClient(BaseClient):
    def __init__(self) -> None:
        super().__init__()
        self.request = APIRequest()

    def get_fixtures_by(
        self,
        season: int = None,
        team_id: int = None,
        ids: List[int] = [],
        league_id: int = None,
        between_dates: Tuple[str, str] = None,
    ) -> Dict[str, Any]:
        endpoint = "/v3/fixtures"
        params = {}

        if season:
            params["season"] = season

        if team_id:
            params["team"] = team_id

        if len(ids):
            params["ids"] = "-".join([str(fix_id) for fix_id in ids])

        if league_id:
            params["league"] = league_id

        if between_dates:
            params["from"] = between_dates[0]
            params["to"] = between_dates[1]

        url = f"{self.base_url}{endpoint}"

        print(params)

        response = self.request.get(url, params, self.headers)

        logger.info(f"get_fixtures_by response - {response.status_code}")

        return response

    def get_head_to_head(self, team_1: str, team_2: str) -> Dict[str, Any]:
        endpoint = "/v3/fixtures/headtohead"
        params = {"h2h": f"{team_1}-{team_2}"}

        url = f"{self.base_url}{endpoint}"

        response = self.request.get(url, params, self.headers)

        logger.info(f"get_fixtures_by response - {response.status_code}")

        return response

    def get_standings_by(self, season: int, team_id: int) -> Dict[str, Any]:
        endpoint = "/v3/standings"
        params = {"season": season, "team": team_id}
        url = f"{self.base_url}{endpoint}"

        return self.request.get(url, params, self.headers)

    def get_team_information(self, team_id: int) -> Dict[str, Any]:
        endpoint = "/v3/teams"
        params = {"id": team_id}
        url = f"{self.base_url}{endpoint}"

        return self.request.get(url, params, self.headers)

    def get_line_up(self, fixture_id: int, team_id: int) -> Dict[str, Any]:
        endpoint = "/v3/fixtures/lineups"
        params = {"fixture": fixture_id, "team": team_id}
        url = f"{self.base_url}{endpoint}"

        return self.request.get(url, params, self.headers)

    def get_leagues(self) -> Dict[str, Any]:
        endpoint = "/v3/leagues"
        url = f"{self.base_url}{endpoint}"
        return self.request.get(url, {}, self.headers)
