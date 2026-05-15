"""ThingsBoard CE REST API client.

Provides authenticated, async HTTP access to the ThingsBoard platform for
telemetry reads, device attribute pushes, and one-way RPC dispatch.

Authentication uses JWT tokens obtained via the ``/api/auth/login`` endpoint.
Tokens are refreshed automatically on 401 responses.  Transient 5xx errors
trigger up to three retries with exponential backoff.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0  # seconds — doubles on each retry


class ThingsBoardClient:
    """Async REST client for the ThingsBoard CE API.

    Authentication credentials and the base URL are loaded from environment
    variables (via :func:`~src.utils.config.get_settings`):

    - ``TB_REST_URL`` — base URL, e.g. ``https://thingsboard.example.com``
    - ``TB_USERNAME`` — ThingsBoard user e-mail
    - ``TB_PASSWORD`` — ThingsBoard user password

    Token refresh is handled transparently; callers do not need to manage auth.
    """

    def __init__(self) -> None:
        self._base_url: str = getattr(
            settings, "tb_rest_url", "https://thingsboard.example.com"
        ).rstrip("/")
        self._username: str = getattr(settings, "tb_username", "")
        self._password: str = getattr(settings, "tb_password", "")
        self._token: str | None = None
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    async def _get_client(self) -> httpx.AsyncClient:
        """Return (or lazily create) the underlying :class:`httpx.AsyncClient`."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(base_url=self._base_url, timeout=30.0)
        return self._client

    async def refresh_token(self) -> None:
        """Re-authenticate with ThingsBoard and update the bearer token.

        Raises:
            httpx.HTTPStatusError: If authentication fails.
        """
        client = await self._get_client()
        start = time.monotonic()
        resp = await client.post(
            "/api/auth/login",
            json={"username": self._username, "password": self._password},
        )
        elapsed = (time.monotonic() - start) * 1000
        resp.raise_for_status()
        self._token = resp.json()["token"]
        logger.info(
            "ThingsBoard token refreshed",
            extra={"elapsed_ms": round(elapsed, 1)},
        )

    def _auth_headers(self) -> dict[str, str]:
        """Return the Authorization header dict for authenticated requests."""
        if not self._token:
            raise RuntimeError(
                "ThingsBoard token not yet obtained — call refresh_token() first"
            )
        return {"X-Authorization": f"Bearer {self._token}"}

    # ------------------------------------------------------------------
    # Request helper with retry + re-auth
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute an authenticated HTTP request with retry logic.

        Retries on 401 (re-authenticates) and transient 5xx errors up to
        ``_MAX_RETRIES`` times with exponential backoff.

        Args:
            method: HTTP method (``GET``, ``POST``, etc.).
            path: URL path relative to the base URL.
            **kwargs: Additional kwargs forwarded to :meth:`httpx.AsyncClient.request`.

        Returns:
            Parsed JSON response body.

        Raises:
            httpx.HTTPStatusError: After exhausting all retries.
        """
        client = await self._get_client()
        if self._token is None:
            await self.refresh_token()

        delay = _RETRY_BASE_DELAY
        last_exc: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            start = time.monotonic()
            try:
                resp = await client.request(
                    method, path, headers=self._auth_headers(), **kwargs
                )
                elapsed = (time.monotonic() - start) * 1000
                logger.debug(
                    "ThingsBoard API call",
                    extra={
                        "method": method,
                        "path": path,
                        "status": resp.status_code,
                        "elapsed_ms": round(elapsed, 1),
                    },
                )
                if resp.status_code == 401:
                    logger.info("Token expired, refreshing and retrying")
                    await self.refresh_token()
                    continue
                resp.raise_for_status()
                return resp.json() if resp.content else {}
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code < 500:
                    raise
                last_exc = exc
                logger.warning(
                    "Transient TB API error, retrying",
                    extra={"attempt": attempt, "status": exc.response.status_code},
                )
            except httpx.RequestError as exc:
                last_exc = exc
                logger.warning(
                    "TB API request error, retrying",
                    extra={"attempt": attempt, "error": str(exc)},
                )
            if attempt < _MAX_RETRIES:
                await asyncio.sleep(delay)
                delay *= 2

        raise RuntimeError(
            f"ThingsBoard API request failed after {_MAX_RETRIES} retries"
        ) from last_exc

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    async def get_site_telemetry(
        self,
        device_id: str,
        keys: list[str],
        start_ts: int,
        end_ts: int,
    ) -> dict[str, Any]:
        """Fetch historical telemetry for a ThingsBoard device.

        Args:
            device_id: ThingsBoard device UUID.
            keys: List of telemetry key names to retrieve.
            start_ts: Start timestamp in milliseconds (epoch).
            end_ts: End timestamp in milliseconds (epoch).

        Returns:
            Dict mapping key names to lists of ``{ts, value}`` dicts.
        """
        keys_param = ",".join(keys)
        path = f"/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"
        return await self._request(
            "GET",
            path,
            params={"keys": keys_param, "startTs": start_ts, "endTs": end_ts},
        )

    async def get_portfolio_summary(self) -> list[dict[str, Any]]:
        """Return all assets under the VPP root asset.

        Returns:
            List of asset dicts from ThingsBoard.
        """
        data = await self._request(
            "GET",
            "/api/tenant/assets",
            params={"pageSize": 1000, "page": 0},
        )
        return data.get("data", [])

    async def send_dispatch_rpc(
        self,
        device_id: str,
        method: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Send a one-way RPC to a ThingsBoard device.

        Args:
            device_id: ThingsBoard device UUID.
            method: RPC method name (e.g. ``set_power``).
            params: Method parameters dict.

        Returns:
            ThingsBoard API response dict.
        """
        return await self._request(
            "POST",
            f"/api/rpc/oneway/{device_id}",
            json={"method": method, "params": params},
        )

    async def push_optimization_result(
        self,
        device_id: str,
        attributes: dict[str, Any],
    ) -> None:
        """Push optimization result attributes to a ThingsBoard device.

        Args:
            device_id: ThingsBoard device UUID.
            attributes: Key-value attribute dict to write to SERVER_SCOPE.
        """
        await self._request(
            "POST",
            f"/api/plugins/telemetry/DEVICE/{device_id}/attributes/SERVER_SCOPE",
            json=attributes,
        )
        logger.info(
            "Optimization result pushed to ThingsBoard",
            extra={"device_id": device_id, "keys": list(attributes.keys())},
        )

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
