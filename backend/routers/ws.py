"""
WebSocket router — real-time traffic broadcasting.

A single TrafficBroadcaster polls the Livebox every 5 s and pushes
deltas to all connected clients, so N browser tabs only ever produce
1 Livebox request per interval.
"""
import asyncio
import logging
import time

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from core.auth import get_session_by_token
from core.session import LiveboxSession

router = APIRouter()
logger = logging.getLogger(__name__)

_POLL_INTERVAL = 1  # seconds
_RX_KEYS = ["RxBytes", "rxBytes", "rx_bytes", "BytesReceived"]
_TX_KEYS = ["TxBytes", "txBytes", "tx_bytes", "BytesSent"]


# ---------------------------------------------------------------------------
# Broadcaster
# ---------------------------------------------------------------------------


def _find_num(obj: dict, keys: list[str]) -> float | None:
    for k in keys:
        v = obj.get(k)
        if v is not None:
            try:
                return float(v)
            except (ValueError, TypeError):
                pass
    return None


class _TrafficBroadcaster:
    """
    Polls HomeLan.getWANCounters once per _POLL_INTERVAL and broadcasts
    the computed byte-rate delta to every connected WebSocket.
    """

    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._session: LiveboxSession | None = None
        self._task: asyncio.Task | None = None  # type: ignore[type-arg]
        self._last_raw: dict | None = None
        self._last_ts: float = 0

    # ------------------------------------------------------------------
    # Client lifecycle
    # ------------------------------------------------------------------

    async def add(self, ws: WebSocket, session: LiveboxSession) -> None:
        await ws.accept()
        self._clients.add(ws)
        if self._session is None:
            self._session = session
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._poll_loop())

    def remove(self, ws: WebSocket) -> None:
        self._clients.discard(ws)

    # ------------------------------------------------------------------
    # Polling loop
    # ------------------------------------------------------------------

    async def _poll_loop(self) -> None:
        while self._clients:
            try:
                await self._tick()
            except Exception as exc:
                logger.warning("Traffic broadcaster error: %s", exc)
            await asyncio.sleep(_POLL_INTERVAL)

    async def _tick(self) -> None:
        if self._session is None:
            return

        data: dict = await self._session.call("HomeLan", "getWANCounters", {})
        now = time.time()
        msg = self._compute_delta(data, now)
        self._last_raw = data
        self._last_ts = now

        if msg is None:
            return

        dead: set[WebSocket] = set()
        for ws in list(self._clients):
            try:
                await ws.send_json(msg)
            except Exception:
                dead.add(ws)
        self._clients -= dead

    def _compute_delta(self, data: dict, now: float) -> dict | None:
        if self._last_raw is None or self._last_ts == 0:
            return None
        dt = now - self._last_ts
        if dt <= 0:
            return None

        inner = data.get("status", data.get("data", data))
        last_inner = self._last_raw.get("status", self._last_raw.get("data", self._last_raw))

        rx = _find_num(inner, _RX_KEYS)
        tx = _find_num(inner, _TX_KEYS)
        last_rx = _find_num(last_inner, _RX_KEYS)
        last_tx = _find_num(last_inner, _TX_KEYS)

        if None in (rx, tx, last_rx, last_tx):
            return None

        return {
            "rxBps": max(0.0, (rx - last_rx) / dt),  # type: ignore[operator]
            "txBps": max(0.0, (tx - last_tx) / dt),  # type: ignore[operator]
            "ts": now,
        }


_broadcaster = _TrafficBroadcaster()


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.websocket("/traffic")
async def ws_traffic(
    websocket: WebSocket,
    token: str = Query(..., description="Bearer token from /api/auth/login"),
) -> None:
    """
    Real-time WAN traffic stream.

    Authenticate by passing the bearer token as a query parameter:
      ws://<host>/api/ws/traffic?token=<token>

    Messages are JSON objects: { rxBps: float, txBps: float, ts: float }
    """
    session = get_session_by_token(token)
    if session is None:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    await _broadcaster.add(websocket, session)
    try:
        # Keep the socket open; we only send, never receive meaningful data.
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        _broadcaster.remove(websocket)
