from __future__ import annotations

import asyncio
from typing import Mapping

import httpx


class RetryHttpClient:
    def __init__(
        self,
        timeout_seconds: float,
        retries: int,
        user_agent: str,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._retries = retries
        self._user_agent = user_agent
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "RetryHttpClient":
        self._client = httpx.AsyncClient(
            timeout=self._timeout_seconds,
            headers={"User-Agent": self._user_agent},
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get(self, url: str, params: Mapping[str, str | int] | None = None) -> str:
        if self._client is None:
            raise RuntimeError("HTTP client is not initialized.")

        attempt = 0
        while True:
            try:
                response = await self._client.get(url, params=params)
                response.raise_for_status()
                return response.text
            except (httpx.HTTPError, httpx.TimeoutException):
                if attempt >= self._retries:
                    raise
                attempt += 1
                await asyncio.sleep(min(2**attempt, 5))
