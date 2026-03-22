from fastapi import APIRouter, Depends

from core.session import LiveboxSession
from core.auth import get_session
from models.device import ExportRequest, RestoreExtendedRequest, RestoreRequest

router = APIRouter()


@router.get("/info")
async def get_info(session: LiveboxSession = Depends(get_session)):
    return await session.call("DeviceInfo", "get", {})


@router.get("/pairing")
async def get_pairing(session: LiveboxSession = Depends(get_session)):
    return await session.call("DeviceInfo", "getPairingInfo", {})


@router.put("")
async def update(session: LiveboxSession = Depends(get_session)):
    return await session.call("DeviceInfo", "update", {})


@router.post("/export")
async def export(body: ExportRequest, session: LiveboxSession = Depends(get_session)):
    return await session.call("DeviceInfo", "export", body.model_dump())


@router.post("/config/restore")
async def restore(body: RestoreRequest, session: LiveboxSession = Depends(get_session)):
    return await session.call(
        "DeviceInfo.VendorConfigFile",
        "Restore",
        body.model_dump(exclude_none=True),
    )


@router.post("/config/restore-extended")
async def restore_extended(
    body: RestoreExtendedRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "DeviceInfo.VendorConfigFile",
        "RestoreExtended",
        body.model_dump(exclude_none=True),
    )
