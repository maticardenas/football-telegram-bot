from dataclasses import dataclass
from typing import Any, Dict

import requests


@dataclass
class Response:
    status_code: int
    text: str
    as_dict: object
    headers: dict


class APIRequest:
    def get(
        self, url: str, params: Dict[Any, Any], headers: Dict[str, str]
    ) -> Response:
        response = requests.get(url, params=params, headers=headers)
        return self.__get_responses(response)

    def post(
        self, url: str, payload: Dict[Any, Any], headers: Dict[str, str]
    ) -> Response:
        response = requests.post(url, data=payload, headers=headers)
        return self.__get_responses(response)

    def put(
        self, url: str, payload: Dict[Any, Any], headers: Dict[str, str]
    ) -> Response:
        response = requests.put(url, data=payload, headers=headers)
        return self.__get_responses(response)

    def delete(self, url: str) -> Response:
        response = requests.delete(url)
        return self.__get_responses(response)

    def __get_responses(self, response: "requests.models.Response") -> Response:
        status_code = response.status_code
        text = response.text

        try:
            as_dict = response.json()
        except Exception:
            as_dict = {}

        headers = response.headers

        return Response(status_code, text, as_dict, headers)
