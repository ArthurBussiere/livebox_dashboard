from fastapi import APIRouter, Depends

from core.session import LiveboxSession
from core.auth import get_session
from models.dhcp import (
    LeaseTimeRequest,
    PoolAssignRequest,
    PoolCreate,
    StaticLeaseCreate,
    StaticLeaseUpdate,
)

router = APIRouter()


@router.get("/leases")
async def get_leases(
    rule: str | None = None, session: LiveboxSession = Depends(get_session)
):
    params = {}
    if rule is not None:
        params["rule"] = rule
    return await session.call("DHCPv4.Server.Pool.default", "getLeases", params)


@router.get("/leases/static")
async def get_static_leases(session: LiveboxSession = Depends(get_session)):
    return await session.call("DHCPv4.Server.Pool.default", "getStaticLeases", {})


@router.post("/leases/static")
async def add_static_lease(
    body: StaticLeaseCreate, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "DHCPv4.Server.Pool.default",
        "addStaticLease",
        body.model_dump(),
    )


@router.put("/leases/static/{mac}")
async def update_static_lease(
    mac: str, body: StaticLeaseUpdate, session: LiveboxSession = Depends(get_session)
):
    params: dict = {"MACAddress": mac}
    if body.IPAddress is not None:
        params["IPAddress"] = body.IPAddress
    if body.Enable is not None:
        params["Enable"] = body.Enable
    return await session.call("DHCPv4.Server.Pool.default", "setStaticLease", params)


@router.delete("/leases/static/{mac}")
async def delete_static_lease(mac: str, session: LiveboxSession = Depends(get_session)):
    return await session.call(
        "DHCPv4.Server.Pool.default", "deleteStaticLease", {"MACAddress": mac}
    )


@router.post("/leases/static/{mac}/renew")
async def renew_lease(mac: str, session: LiveboxSession = Depends(get_session)):
    return await session.call("DHCPv4.Server.Pool.default.Rule.Lease", "forceRenew", {})


@router.post("/leases/pool-assign")
async def assign_from_pool(
    body: PoolAssignRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "DHCPv4.Server.Pool.default", "addLeaseFromPool", body.model_dump()
    )


@router.put("/lease-time")
async def set_lease_time(
    body: LeaseTimeRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "DHCPv4.Server.Pool.default", "setLeaseTime", body.model_dump()
    )


@router.get("/pool/{id}")
async def get_pool(id: str, session: LiveboxSession = Depends(get_session)):
    return await session.call("DHCPv4.Server", "getDHCPServerPool", {"id": id})


@router.post("/pool")
async def create_pool(body: PoolCreate, session: LiveboxSession = Depends(get_session)):
    return await session.call(
        "DHCPv4.Server",
        "createPool",
        body.model_dump(),
    )


@router.delete("/stats")
async def clear_stats(session: LiveboxSession = Depends(get_session)):
    return await session.call("DHCPv4.Server", "clearStatistics", {})


@router.get("/stats/dora")
async def get_dora_cycles(session: LiveboxSession = Depends(get_session)):
    return await session.call("DHCPv4.Server.Stats", "getDoraCyclesDetails", {})
