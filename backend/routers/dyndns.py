from fastapi import APIRouter, Depends

from core.session import LiveboxSession
from core.auth import get_session
from models.dyndns import DynDNSEnableRequest, DynDNSHostCreate

router = APIRouter()


@router.get("")
async def get_hosts(session: LiveboxSession = Depends(get_session)):
    return await session.call("DynDNS", "getHosts", {})


@router.post("")
async def add_host(body: DynDNSHostCreate, session: LiveboxSession = Depends(get_session)):
    return await session.call("DynDNS", "addHost", body.model_dump(exclude_none=True))


@router.delete("/{hostname}")
async def delete_host(hostname: str, session: LiveboxSession = Depends(get_session)):
    return await session.call("DynDNS", "delHost", {"hostname": hostname})


@router.get("/services")
async def get_services(session: LiveboxSession = Depends(get_session)):
    return await session.call("DynDNS", "getServices", {})


@router.get("/enable")
async def get_global_enable(session: LiveboxSession = Depends(get_session)):
    return await session.call("DynDNS", "getGlobalEnable", {})


@router.patch("/enable")
async def set_global_enable(
    body: DynDNSEnableRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call("DynDNS", "setGlobalEnable", {"enable": body.enable})


@router.get("/cgnat")
async def get_cgnat(session: LiveboxSession = Depends(get_session)):
    return await session.call("DynDNS", "getEnableOnCgnat", {})


@router.patch("/cgnat")
async def set_cgnat(
    body: DynDNSEnableRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call("DynDNS", "setEnableOnCgnat", {"value": body.enable})
