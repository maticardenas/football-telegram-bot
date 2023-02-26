from typing import Optional

import httpx
from httpx import HTTPStatusError
from pydantic import BaseModel
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_fixed

from config.notif_config import NotifConfig
from src.notifier_constants import MAX_RETRY_ATTEMPTS, TIME_OUT, WAIT_BETWEEN_REQUESTS
from src.notifier_logger import get_logger

logger = get_logger(__name__)


class Response(BaseModel):
    status_code: int
    text: str
    as_dict: object
    headers: dict


class BaseClient:
    _client = None

    def __init__(
        self,
        share_session: bool = False,
        raise_for_status: bool = False,
        perform_retries: bool = False,
    ) -> None:
        self.base_url = f"https://{NotifConfig.X_RAPIDAPI_HOST}"
        self.headers = {
            "x-rapidapi-host": NotifConfig.X_RAPIDAPI_HOST,
            "x-rapidapi-key": NotifConfig.X_RAPIDAPI_KEY,
        }
        self._share_session = share_session
        self._raise_for_status = raise_for_status
        self._perform_retries = perform_retries

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

        for attempt in Retrying(
            stop=stop_after_attempt(MAX_RETRY_ATTEMPTS if self._perform_retries else 1),
            wait=wait_fixed(WAIT_BETWEEN_REQUESTS),
            retry=retry_if_exception_type(HTTPStatusError),
        ):
            with attempt:
                response = self.client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=TIME_OUT,
                    **kwargs,
                )

                if self._raise_for_status:
                    response.raise_for_status()

        return Response(
            status_code=response.status_code,
            text=response.text,
            as_dict=response.json(),
            headers=response.headers,
        )
