from fastapi import APIRouter, Depends

from core.session import LiveboxSession
from core.auth import get_session
from models.wifi import (
    GuestConfig,
    WifiConfig,
    WifiEnableRequest,
    WifiPairingRequest,
    WifiStatusRequest,
)

router = APIRouter()


@router.get("")
async def get_wifi(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.Wifi", "get", {})


@router.put("")
async def set_wifi(body: WifiConfig, session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.Wifi", "set", body.model_dump(exclude_none=True))


@router.patch("/enable")
async def set_enable(body: WifiEnableRequest, session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.Wifi", "setEnable", body.model_dump(exclude_none=True))


@router.post("/enable/toggle")
async def toggle_enable(
    body: WifiEnableRequest | None = None, session: LiveboxSession = Depends(get_session)
):
    params = body.model_dump(exclude_none=True) if body else {}
    return await session.call("NMC.Wifi", "toggleEnable", params)


@router.patch("/status")
async def set_status(
    body: WifiStatusRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call("NMC.Wifi", "setStatus", {"Status": body.Status})


@router.get("/stats")
async def get_stats(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.Wifi", "getStats", {})


@router.post("/channel/auto")
async def start_auto_channel(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.Wifi", "startAutoChannelSelection", {})


@router.post("/pairing/start")
async def start_pairing(
    body: WifiPairingRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call("NMC.Wifi", "startPairing", {"clientPIN": body.clientPIN})


@router.post("/pairing/stop")
async def stop_pairing(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.Wifi", "stopPairing", {})


@router.post("/wps/pin")
async def generate_wps_pin(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.Wifi.WPS", "generateSelfPIN", {})


@router.get("/guest")
async def get_guest(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.Guest", "get", {})


@router.put("/guest")
async def set_guest(body: GuestConfig, session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.Guest", "set", {"Enable": body.Enable})
