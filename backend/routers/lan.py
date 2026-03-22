from fastapi import APIRouter, Depends

from core.session import LiveboxSession
from core.auth import get_session
from models.lan import DeviceStatsRequest, LanStatsRequest, MonitoringTestRequest

router = APIRouter()


@router.get("/status")
async def get_status(session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "getStatus", {})


@router.get("/interfaces")
async def get_interfaces(session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "getInterfacesNames", {})


@router.get("/devices")
async def get_devices(session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "getDevicesNames", {})


@router.get("/devices/status")
async def get_devices_status(session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "getDevicesStatus", {})


@router.get("/wan-counters")
async def get_wan_counters(session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "getWANCounters", {})


@router.get("/saturation")
async def get_saturation(session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "getSaturationResults", {})


@router.get("/saturation/measures")
async def get_saturation_measures(session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "getSaturationMeasures", {})


@router.get("/stats")
async def get_stats(body: LanStatsRequest, session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "getResults", body.model_dump(exclude_none=True))


@router.get("/stats/device")
async def get_device_stats(
    body: DeviceStatsRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "HomeLan", "getDeviceResults", body.model_dump(exclude_none=True)
    )


@router.post("/devices/{mac}")
async def add_device(mac: str, session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "addDevice", {"macaddress": mac})


@router.delete("/devices/{mac}")
async def delete_device(mac: str, session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "deleteDevice", {"macaddress": mac})


@router.post("/monitoring/interface/start")
async def start_interface_monitoring(
    body: MonitoringTestRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "HomeLan",
        "startInterfaceMonitoringTest",
        body.model_dump(),
    )


@router.post("/monitoring/interface/stop")
async def stop_interface_monitoring(session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "stopInterfaceMonitoringTest", {})


@router.post("/monitoring/device/start")
async def start_device_monitoring(
    body: MonitoringTestRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "HomeLan",
        "startDeviceMonitoringTest",
        body.model_dump(),
    )


@router.post("/monitoring/device/stop")
async def stop_device_monitoring(session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "stopDeviceMonitoringTest", {})


@router.get("/config/export")
async def export_config(session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "export", {})


@router.post("/config/import")
async def import_config(session: LiveboxSession = Depends(get_session)):
    return await session.call("HomeLan", "import", {})
