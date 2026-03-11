from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

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

    def dispatch_via_browser(
        self,
        *,
        task_url: str,
        api_root: str,
        task_id: str,
        route_path: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            from playwright.sync_api import sync_playwright
        except ModuleNotFoundError as exc:
            raise TransportError("Browser fallback requires playwright to be installed") from exc

        if not route_path.startswith("/"):
            route_path = "/" + route_path

        storage_state: dict[str, Any] = {"cookies": [], "origins": []}
        for cookie in self.session.cookies:
            domain = cookie.domain or urlparse(self.base_url).hostname or ""
            storage_state["cookies"].append(
                {
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": domain.lstrip("."),
                    "path": cookie.path or "/",
                    "expires": float(cookie.expires) if cookie.expires else -1,
                    "httpOnly": False,
                    "secure": bool(cookie.secure),
                    "sameSite": "Lax",
                }
            )

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                base_url=self.base_url,
                user_agent=self.user_agent,
                storage_state=storage_state,
            )
            page = context.new_page()
            try:
                page.goto(task_url, wait_until="domcontentloaded", timeout=30000)
                response = page.evaluate(
                    """async ({ apiRoot, taskId, endpoint, body }) => {
                        if (!window.erc32 || typeof window.erc32.dispatch !== 'function') {
                            throw new Error('window.erc32.dispatch is unavailable');
                        }
                        return await window.erc32.dispatch(apiRoot, taskId, endpoint, body);
                    }""",
                    {
                        "apiRoot": api_root,
                        "taskId": task_id,
                        "endpoint": route_path,
                        "body": body,
                    },
                )
            except Exception as exc:  # noqa: BLE001
                raise TransportError(f"Browser dispatch failed for {route_path}: {exc}") from exc
            finally:
                context.close()
                browser.close()

        return response if isinstance(response, dict) else {"result": response}

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