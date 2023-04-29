from typing import Any, Dict, Optional

from src.api.base_client import BaseClient


class TelegramClient(BaseClient):
    def __init__(self, token: str) -> None:
        super().__init__()
        self._token = token
        self.base_url = "https://api.telegram.org"

    def send_message(self, chat_id: str, msg: str) -> Dict[str, Any]:
        endpoint = f"/bot{self._token}/sendMessage"
        params = {"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}
        url = f"{self.base_url}{endpoint}"

        return self._request(
            url=url, method="POST", params=params, headers=self.headers
        )

    def send_photo(
        self,
        chat_id: str,
        photo_id=None,
        photo_url: Optional[str] = None,
        text: Optional[str] = "",
    ) -> Dict[str, Any]:
        photo = photo_id if photo_id else photo_url
        endpoint = f"/bot{self._token}/sendPhoto"
        params = {
            "chat_id": chat_id,
            "photo": photo,
            "caption": text,
            "parse_mode": "HTML",
        }
        url = f"{self.base_url}{endpoint}"

        return self._request(
            url=url, method="POST", params=params, headers=self.headers
        )

    def send_video(
        self,
        chat_id: str,
        video_url: str,
        text: Optional[str] = "",
    ) -> Dict[str, Any]:
        endpoint = f"/bot{self._token}/sendVideo"
        params = {
            "chat_id": chat_id,
            "video": video_url,
            # "caption": text,
            # "parse_mode": "markdown",
        }
        url = f"{self.base_url}{endpoint}"

        return self._request(
            url=url, method="POST", params=params, headers=self.headers
        )
