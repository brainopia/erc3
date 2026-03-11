from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from .errors import TransportError


@dataclass(slots=True)
class BrowserRuntime:
    session: requests.Session
    base_url: str = "https://erc.timetoact-group.at"
    user_agent: str = "erc3-live-wrapper/0.1"

    def fetch_text(self, path: str) -> str:
        response = self.session.get(self._url(path), timeout=30)
        self._raise_for_status(response)
        return response.text

    def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.session.post(self._url(path), json=payload, timeout=30)
        self._raise_for_status(response)
        return response.json()

    def close(self) -> None:
        self.session.close()

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            detail = response.text.strip()
            message = str(exc) if not detail else f"{exc}: {detail}"
            raise TransportError(message) from exc
