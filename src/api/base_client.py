from typing import Optional

import httpx
from pydantic import BaseModel

from config.notif_config import NotifConfig
from src.notifier_constants import TIME_OUT
from src.notifier_logger import get_logger

logger = get_logger(__name__)


class Response(BaseModel):
    status_code: int
    text: str
    as_dict: object
    headers: dict


class BaseClient:
    _client = None

    def __init__(self, share_session: bool = False) -> None:
        self.base_url = f"https://{NotifConfig.X_RAPIDAPI_HOST}"
        self.headers = {
            "x-rapidapi-host": NotifConfig.X_RAPIDAPI_HOST,
            "x-rapidapi-key": NotifConfig.X_RAPIDAPI_KEY,
        }
        self._share_session = share_session

    @property
    def client(self) -> httpx.Client:
        if self._share_session is False:
            return httpx.Client()
        if not self._client:
            self._client = httpx.Client()
        return self._client

    @client.setter
    def client(self, value: Optional[httpx.Client]) -> None:
        self._client = value

    def _request(self, method: str, url: str, headers: dict, **kwargs) -> "Response":
        logger.info(
            f"Request {' - '.join(filter(None, [method, url, str(kwargs.get('params', ''))]))}"
        )
        response = self.client.request(
            method=method,
            url=url,
            headers=headers,
            timeout=TIME_OUT,
            **kwargs,
        )

        return Response(
            status_code=response.status_code,
            text=response.text,
            as_dict=response.json(),
            headers=response.headers,
        )
