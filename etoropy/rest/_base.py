from __future__ import annotations

from typing import Any

from ..http.client import HttpClient, RequestOptions


class BaseRestClient:
    """Base class for all REST sub-clients, providing ``_get``/``_post``/``_put``/``_delete`` helpers."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def _get(self, path: str, query: dict[str, Any] | None = None) -> Any:
        return await self._http.request(RequestOptions(method="GET", path=path, query=query))

    async def _post(self, path: str, body: Any = None) -> Any:
        return await self._http.request(RequestOptions(method="POST", path=path, body=body))

    async def _put(self, path: str, body: Any = None) -> Any:
        return await self._http.request(RequestOptions(method="PUT", path=path, body=body))

    async def _delete(self, path: str, body: Any = None) -> Any:
        return await self._http.request(RequestOptions(method="DELETE", path=path, body=body))
