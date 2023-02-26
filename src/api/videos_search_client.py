from typing import Any, Dict

import httpx

from config.notif_config import NotifConfig


class VideosSearchClient:
    def __init__(self) -> None:
        super().__init__()
        self.base_url = f"https://{NotifConfig.X_RAPIDAPI_VIDEO_SEARCH_HOST}"
        self.headers = {
            "x-rapidapi-host": NotifConfig.X_RAPIDAPI_VIDEO_SEARCH_HOST,
            "x-rapidapi-key": NotifConfig.X_RAPIDAPI_KEY,
        }

    def search_football_videos(self) -> Dict[str, Any]:
        return httpx.get(self.base_url, {}, self.headers)
