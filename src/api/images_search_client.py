from typing import Any, Dict

import httpx

from config.notif_config import NotifConfig


class ImagesSearchClient:
    def __init__(self) -> None:
        super().__init__()
        self.base_url = f"https://{NotifConfig.X_RAPIDAPI_IMG_SEARCH_HOST}"
        self.headers = {
            "x-rapidapi-host": NotifConfig.X_RAPIDAPI_IMG_SEARCH_HOST,
            "x-rapidapi-key": NotifConfig.X_RAPIDAPI_KEY,
        }
        self.endpoint = "/images/search"

    def get_images(self, search_query: str) -> Dict[str, Any]:
        params = {"q": search_query}
        url = f"{self.base_url}{self.endpoint}"

        return httpx.get(url, params, self.headers)
