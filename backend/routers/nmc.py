from typing import Any

from fastapi import APIRouter, Depends

from core.session import LiveboxSession
from core.auth import get_session
from models.nmc import (
    BackupRequest,
    ContainerNetworkConfig,
    IPTVMultiscreenRequest,
    IPv6Config,
    LanIPConfig,
    LedConfig,
    NetworkBRRequest,
    RebootRequest,
    RemoteAccessCreate,
    RemoteAccessDisable,
    WanModeRequest,
    WlanTimerRequest,
)

router = APIRouter()

# ---------------------------------------------------------------------------
# Core config
# ---------------------------------------------------------------------------


@router.get("")
async def get_nmc(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC", "get", {})


@router.put("")
async def set_nmc(body: dict[str, Any], session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC", "set", body)


# ---------------------------------------------------------------------------
# System control
# ---------------------------------------------------------------------------


@router.post("/reboot")
async def reboot(body: RebootRequest, session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC", "reboot", {"reason": body.reason})


@router.post("/reset")
async def reset(body: RebootRequest, session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC", "reset", {"reason": body.reason})


@router.post("/shutdown")
async def shutdown(body: RebootRequest, session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC", "shutdown", {"reason": body.reason})


# ---------------------------------------------------------------------------
# WAN
# ---------------------------------------------------------------------------


@router.get("/wan/status")
async def get_wan_status(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC", "getWANStatus", {})


@router.get("/wan/modes")
async def get_wan_modes(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC", "getWanModeList", {})


@router.put("/wan/mode")
async def set_wan_mode(body: WanModeRequest, session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC", "setWanMode", body.model_dump(exclude_none=True))


# ---------------------------------------------------------------------------
# LAN IP
# ---------------------------------------------------------------------------


@router.get("/lan-ip")
async def get_lan_ip(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC", "getLANIP", {})


@router.put("/lan-ip")
async def set_lan_ip(body: LanIPConfig, session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC", "setLANIP", body.model_dump(exclude_none=True))


# ---------------------------------------------------------------------------
# Remote access
# ---------------------------------------------------------------------------


@router.get("/remote-access")
async def get_remote_access(
    username: str | None = None,
    usertype: str | None = None,
    session: LiveboxSession = Depends(get_session),
):
    params = {}
    if username is not None:
        params["username"] = username
    if usertype is not None:
        params["usertype"] = usertype
    return await session.call("NMC", "getRemoteAccess", params)


@router.post("/remote-access")
async def enable_remote_access(
    body: RemoteAccessCreate, session: LiveboxSession = Depends(get_session)
):
    return await session.call("NMC", "enableRemoteAccess", body.model_dump(exclude_none=True))


@router.delete("/remote-access")
async def disable_remote_access(
    body: RemoteAccessDisable, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "NMC", "disableRemoteAccess", body.model_dump(exclude_none=True)
    )


# ---------------------------------------------------------------------------
# Firmware
# ---------------------------------------------------------------------------


@router.post("/firmware/version")
async def update_version_info(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC", "updateVersionInfo", {})


@router.get("/firmware/check")
async def check_upgrades(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC", "checkForUpgrades", {})


# ---------------------------------------------------------------------------
# IPv6
# ---------------------------------------------------------------------------


@router.get("/ipv6")
async def get_ipv6(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.IPv6", "get", {})


@router.put("/ipv6")
async def set_ipv6(body: IPv6Config, session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.IPv6", "set", body.model_dump(exclude_none=True))


# ---------------------------------------------------------------------------
# IPTV
# ---------------------------------------------------------------------------


@router.get("/iptv/config")
async def get_iptv_config(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.OrangeTV", "getIPTVConfig", {})


@router.get("/iptv/status")
async def get_iptv_status(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.OrangeTV", "getIPTVStatus", {})


@router.get("/iptv/multiscreen")
async def get_iptv_multiscreen(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.OrangeTV", "getIPTVMultiScreens", {})


@router.put("/iptv/multiscreen")
async def set_iptv_multiscreen(
    body: IPTVMultiscreenRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "NMC.OrangeTV", "setIPTVMultiScreens", {"Enable": body.Enable}
    )


# ---------------------------------------------------------------------------
# LED
# ---------------------------------------------------------------------------


@router.get("/led/{name}")
async def get_led(name: str, session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.LED", "getLedStatus", {"name": name})


@router.put("/led/{name}")
async def set_led(
    name: str, body: LedConfig, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "NMC.LED", "setLed", {"name": name, "state": body.state, "color": body.color}
    )


# ---------------------------------------------------------------------------
# Container network
# ---------------------------------------------------------------------------


@router.get("/container")
async def get_container(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.Container", "get", {})


@router.put("/container")
async def set_container(
    body: ContainerNetworkConfig, session: LiveboxSession = Depends(get_session)
):
    return await session.call("NMC.Container", "set", body.model_dump(exclude_none=True))


# ---------------------------------------------------------------------------
# Network backup / restore
# ---------------------------------------------------------------------------


@router.get("/network-config")
async def get_network_config(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.NetworkConfig", "get", {})


@router.post("/network-config/backup")
async def launch_backup(
    body: BackupRequest | None = None, session: LiveboxSession = Depends(get_session)
):
    params = body.model_dump(exclude_none=True) if body else {}
    return await session.call("NMC.NetworkConfig", "launchNetworkBackup", params)


@router.post("/network-config/restore")
async def launch_restore(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC.NetworkConfig", "launchNetworkRestore", {})


@router.patch("/network-config/bridge")
async def set_network_br(
    body: NetworkBRRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "NMC.NetworkConfig", "enableNetworkBR", body.model_dump(exclude_none=True)
    )


# ---------------------------------------------------------------------------
# WiFi timer
# ---------------------------------------------------------------------------


@router.get("/wlan-timer/{interface}")
async def get_wlan_timer(interface: str, session: LiveboxSession = Depends(get_session)):
    return await session.call(
        "NMC.WlanTimer", "getActivationTimer", {"InterfaceName": interface}
    )


@router.put("/wlan-timer/{interface}")
async def set_wlan_timer(
    interface: str,
    body: WlanTimerRequest,
    session: LiveboxSession = Depends(get_session),
):
    return await session.call(
        "NMC.WlanTimer",
        "setActivationTimer",
        {"InterfaceName": interface, "Timeout": body.Timeout},
    )


@router.delete("/wlan-timer/{interface}")
async def disable_wlan_timer(
    interface: str, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "NMC.WlanTimer", "disableActivationTimer", {"InterfaceName": interface}
    )
