from typing import Any, Dict, List

from config.notif_config import NotifConfig
from src.request import APIRequest


class YoutubeSearchClient:
    def __init__(self) -> None:
        super().__init__()
        self.base_url = (
            f"https://{NotifConfig.X_YOUTUBE_SEARCH_HOST}/get_keywords_video/v1"
        )
        self.headers = {
            "content-type": "application/x-www-form-urlencoded",
            "x-rapidapi-host": NotifConfig.X_YOUTUBE_SEARCH_HOST,
            "x-rapidapi-key": NotifConfig.X_RAPIDAPI_KEY,
        }
        self.request = APIRequest()

    def search_videos_by_keywords(
        self, query: List[str], language: str, region: str
    ) -> Dict[str, Any]:
        params = f"keywords=%5B%22{'%22%2C%22'.join(query)}%22%5D&language={language}&region={region}"

        return self.request.post(self.base_url, params, self.headers)
