import logging

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)

_CONTENT_TYPE = "application/x-sah-ws-4-call+json"
_WS_PATH = "/ws"
_AUTH_SERVICE = "sah.Device.Information"
_AUTH_METHOD = "createContext"
_APP_NAME = "so_sdkut"

# Livebox status codes that map to HTTP errors
_STATUS_PERMISSION_DENIED = 13   # "Permission denied"
_STATUS_INVALID_PARAM = 9        # "Invalid parameter"
_STATUS_NOT_FOUND = 16           # "Object not found" (varies by firmware)


class LiveboxSession:
    """
    Async wrapper around the Livebox JSON-RPC API.

    Authentication flow:
      POST /ws  service=sah.Device.Information  method=createContext
      → response["data"]["contextID"]  used as bearer token in every subsequent call.

    Re-authentication is attempted automatically on a 401 HTTP response.
    """

    def __init__(self, url: str, user: str, password: str, timeout: float = 10.0) -> None:
        self._url = url.rstrip("/")
        self._user = user
        self._password = password
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._token: str | None = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _client_instance(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._url,
                timeout=self._timeout,
            )
        return self._client

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": _CONTENT_TYPE}
        if self._token:
            headers["Authorization"] = f"X-Sah {self._token}"
        return headers

    @staticmethod
    def _raise_for_livebox_error(data: dict) -> None:
        """
        Translate Livebox error payloads into HTTPExceptions.

        The box signals errors in two ways:
          1. A non-empty "errors" list in the response body.
          2. A numeric "status" field with a known error code.
        """
        # --- errors array ---
        errors = data.get("errors") or []
        if errors:
            error = errors[0] if isinstance(errors, list) else errors
            msg = (
                error.get("description", str(error))
                if isinstance(error, dict)
                else str(error)
            )
            msg_lower = msg.lower()
            if "permission" in msg_lower or "denied" in msg_lower:
                raise HTTPException(status_code=403, detail=msg)
            if "not found" in msg_lower or "unknown" in msg_lower:
                raise HTTPException(status_code=404, detail=msg)
            raise HTTPException(status_code=502, detail=msg)

        # --- numeric status code ---
        status = data.get("status")
        if isinstance(status, int) and status != 0:
            if status == _STATUS_PERMISSION_DENIED:
                raise HTTPException(status_code=403, detail="Permission denied")
            if status == _STATUS_INVALID_PARAM:
                raise HTTPException(status_code=422, detail="Invalid parameter")
            if status == _STATUS_NOT_FOUND:
                raise HTTPException(status_code=404, detail="Object not found")
            if status < 0:
                raise HTTPException(
                    status_code=502, detail=f"Livebox error (status={status})"
                )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def signin(self) -> None:
        """Authenticate against the Livebox and store the context token."""
        client = self._client_instance()
        try:
            response = await client.post(
                _WS_PATH,
                headers={
                    "Content-Type": _CONTENT_TYPE,
                    "Authorization": "X-Sah-Login",
                },
                json={
                    "service": _AUTH_SERVICE,
                    "method": _AUTH_METHOD,
                    "parameters": {
                        "applicationName": _APP_NAME,
                        "username": self._user,
                        "password": self._password,
                    },
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502, detail=f"Livebox unreachable: {exc}"
            ) from exc

        data = response.json()
        self._token = (data.get("data") or {}).get("contextID")
        if not self._token:
            raise HTTPException(status_code=401, detail="Livebox authentication failed")

    async def _post(self, payload: dict) -> "httpx.Response":
        """Send a single JSON-RPC POST, raising 502 on network error."""
        try:
            return await self._client_instance().post(
                _WS_PATH, headers=self._headers(), json=payload
            )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502, detail=f"Livebox unreachable: {exc}"
            ) from exc

    @staticmethod
    def _is_permission_denied(data: dict) -> bool:
        """Return True when the Livebox signals an expired/invalid session.

        The box never returns HTTP 401 for token expiry — it returns HTTP 200
        with either a numeric status of 13 ("Permission denied") or an errors
        array whose first entry contains the word "permission" or "denied".
        Both cases require a re-authentication.
        """
        if data.get("status") == _STATUS_PERMISSION_DENIED:
            return True
        errors = data.get("errors") or []
        first = (errors[0] if isinstance(errors, list) else errors) if errors else None
        if isinstance(first, dict):
            msg = first.get("description", "").lower()
            return "permission" in msg or "denied" in msg
        return False

    async def call(
        self,
        service: str,
        method: str,
        parameters: dict | None = None,
    ) -> dict:
        """
        Execute a single JSON-RPC call.
        Re-authenticates once on:
          - HTTP 401 (rare, defensive)
          - Livebox status 13 / "Permission denied" in the body (session expiry)
        """
        if parameters is None:
            parameters = {}

        payload = {"service": service, "method": method, "parameters": parameters}

        response = await self._post(payload)

        # HTTP-level session expiry
        if response.status_code == 401:
            await self.signin()
            response = await self._post(payload)

        if response.status_code not in (200, 201):
            raise HTTPException(
                status_code=response.status_code, detail=response.text
            )

        data: dict = response.json()

        # JSON-level session expiry (status 13 / "Permission denied")
        if self._is_permission_denied(data):
            await self.signin()
            response = await self._post(payload)
            if response.status_code not in (200, 201):
                raise HTTPException(
                    status_code=response.status_code, detail=response.text
                )
            data = response.json()

        self._raise_for_livebox_error(data)
        logger.debug("%s.%s → %s", service, method, data)
        return data

    async def raw_call(self, service: str, method: str, parameters: dict | None = None) -> dict:
        """Like call() but returns the raw Livebox JSON without raising on errors."""
        if parameters is None:
            parameters = {}
        payload = {"service": service, "method": method, "parameters": parameters}
        if not self._token:
            await self.signin()
        response = await self._post(payload)
        if response.status_code == 401:
            await self.signin()
            response = await self._post(payload)
        try:
            return response.json()
        except Exception:
            return {"http_status": response.status_code, "text": response.text}

    async def close(self) -> None:
        """Release the underlying HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._token = None
