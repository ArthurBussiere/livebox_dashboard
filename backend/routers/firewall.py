from fastapi import APIRouter, Depends

from core.session import LiveboxSession
from core.auth import get_session
from models.firewall import (
    CustomRuleCreate,
    DMZCreate,
    FirewallLevelRequest,
    ListEntryCreate,
    PinholeCreate,
    PingRequest,
    PortForwardingCreate,
    PortForwardingEnableRequest,
    PortForwardingRefreshRequest,
    PortForwardingUpdate,
    ProtocolForwardingCreate,
    RedirectCreate,
)

router = APIRouter()

# ---------------------------------------------------------------------------
# Firewall level
# ---------------------------------------------------------------------------


@router.get("/level")
async def get_level(session: LiveboxSession = Depends(get_session)):
    return await session.call("Firewall", "getFirewallLevel", {})


@router.put("/level")
async def set_level(body: FirewallLevelRequest, session: LiveboxSession = Depends(get_session)):
    return await session.call("Firewall", "setFirewallLevel", {"level": body.level})


@router.get("/ipv6-level")
async def get_ipv6_level(session: LiveboxSession = Depends(get_session)):
    return await session.call("Firewall", "getFirewallIPv6Level", {})


@router.put("/ipv6-level")
async def set_ipv6_level(
    body: FirewallLevelRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call("Firewall", "setFirewallIPv6Level", {"level": body.level})


@router.post("/commit")
async def commit(session: LiveboxSession = Depends(get_session)):
    return await session.call("Firewall", "commit", {})


# ---------------------------------------------------------------------------
# Ping
# ---------------------------------------------------------------------------


@router.get("/ping/{interface}")
async def get_ping(interface: str, session: LiveboxSession = Depends(get_session)):
    return await session.call("Firewall", "getRespondToPing", {"sourceInterface": interface})


@router.put("/ping/{interface}")
async def set_ping(
    interface: str, body: PingRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Firewall",
        "setRespondToPing",
        {"sourceInterface": interface, "service_enable": body.service_enable},
    )


# ---------------------------------------------------------------------------
# Port Forwarding
# ---------------------------------------------------------------------------


@router.get("/port-forwarding")
async def get_port_forwarding(
    id: str | None = None, session: LiveboxSession = Depends(get_session)
):
    params = {}
    if id is not None:
        params["id"] = id
    return await session.call("Firewall", "getPortForwarding", params)


@router.post("/port-forwarding")
async def create_port_forwarding(
    body: PortForwardingCreate, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Firewall", "setPortForwarding", body.model_dump(exclude_none=True)
    )


@router.put("/port-forwarding/{id}")
async def update_port_forwarding(
    id: str, body: PortForwardingUpdate, session: LiveboxSession = Depends(get_session)
):
    params = body.model_dump(exclude_none=True)
    params["id"] = id
    return await session.call("Firewall", "setPortForwarding", params)


@router.delete("/port-forwarding/{id}")
async def delete_port_forwarding(
    id: str, origin: str, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Firewall", "deletePortForwarding", {"id": id, "origin": origin}
    )


@router.patch("/port-forwarding/{id}/enable")
async def enable_port_forwarding(
    id: str,
    body: PortForwardingEnableRequest,
    session: LiveboxSession = Depends(get_session),
):
    return await session.call(
        "Firewall",
        "enablePortForwarding",
        {"id": id, "origin": body.origin, "enable": body.enable},
    )


@router.post("/port-forwarding/{id}/refresh")
async def refresh_port_forwarding(
    id: str,
    body: PortForwardingRefreshRequest,
    session: LiveboxSession = Depends(get_session),
):
    params = body.model_dump(exclude_none=True)
    params["id"] = id
    return await session.call("Firewall", "refreshPortForwarding", params)


# ---------------------------------------------------------------------------
# Protocol Forwarding
# ---------------------------------------------------------------------------


@router.get("/protocol-forwarding")
async def get_protocol_forwarding(
    id: str | None = None, session: LiveboxSession = Depends(get_session)
):
    params = {}
    if id is not None:
        params["id"] = id
    return await session.call("Firewall", "getProtocolForwarding", params)


@router.post("/protocol-forwarding")
async def create_protocol_forwarding(
    body: ProtocolForwardingCreate, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Firewall", "setProtocolForwarding", body.model_dump(exclude_none=True)
    )


@router.delete("/protocol-forwarding/{id}")
async def delete_protocol_forwarding(
    id: str, session: LiveboxSession = Depends(get_session)
):
    return await session.call("Firewall", "deleteProtocolForwarding", {"id": id})


# ---------------------------------------------------------------------------
# Pinhole (IPv6)
# ---------------------------------------------------------------------------


@router.get("/pinhole")
async def get_pinhole(
    id: str | None = None,
    origin: str | None = None,
    session: LiveboxSession = Depends(get_session),
):
    params = {}
    if id is not None:
        params["id"] = id
    if origin is not None:
        params["origin"] = origin
    return await session.call("Firewall", "getPinhole", params)


@router.post("/pinhole")
async def create_pinhole(
    body: PinholeCreate, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Firewall", "setPinhole", body.model_dump(exclude_none=True)
    )


@router.delete("/pinhole/{id}")
async def delete_pinhole(
    id: str, origin: str, session: LiveboxSession = Depends(get_session)
):
    return await session.call("Firewall", "deletePinhole", {"id": id, "origin": origin})


# ---------------------------------------------------------------------------
# DMZ
# ---------------------------------------------------------------------------


@router.get("/dmz")
async def get_dmz(id: str | None = None, session: LiveboxSession = Depends(get_session)):
    params = {}
    if id is not None:
        params["id"] = id
    return await session.call("Firewall", "getDMZ", params)


@router.post("/dmz")
async def create_dmz(body: DMZCreate, session: LiveboxSession = Depends(get_session)):
    return await session.call(
        "Firewall", "setDMZ", body.model_dump(exclude_none=True)
    )


@router.delete("/dmz/{id}")
async def delete_dmz(id: str, session: LiveboxSession = Depends(get_session)):
    return await session.call("Firewall", "deleteDMZ", {"id": id})


# ---------------------------------------------------------------------------
# Redirect
# ---------------------------------------------------------------------------


@router.get("/redirect")
async def get_redirect(id: str | None = None, session: LiveboxSession = Depends(get_session)):
    params = {}
    if id is not None:
        params["id"] = id
    return await session.call("Firewall", "getRedirect", params)


@router.post("/redirect")
async def create_redirect(
    body: RedirectCreate, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Firewall", "setRedirect", body.model_dump(exclude_none=True)
    )


@router.delete("/redirect/{id}")
async def delete_redirect(id: str, session: LiveboxSession = Depends(get_session)):
    return await session.call("Firewall", "deleteRedirect", {"id": id})


# ---------------------------------------------------------------------------
# Custom Rules
# ---------------------------------------------------------------------------


@router.get("/custom-rules")
async def get_custom_rules(
    id: str | None = None,
    chain: str | None = None,
    session: LiveboxSession = Depends(get_session),
):
    params = {}
    if id is not None:
        params["id"] = id
    if chain is not None:
        params["chain"] = chain
    return await session.call("Firewall", "getCustomRule", params)


@router.post("/custom-rules")
async def create_custom_rule(
    body: CustomRuleCreate, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Firewall", "setCustomRule", body.model_dump(exclude_none=True)
    )


@router.delete("/custom-rules/{id}")
async def delete_custom_rule(
    id: str, chain: str | None = None, session: LiveboxSession = Depends(get_session)
):
    params: dict = {"id": id}
    if chain is not None:
        params["chain"] = chain
    return await session.call("Firewall", "deleteCustomRule", params)


# ---------------------------------------------------------------------------
# List Entries
# ---------------------------------------------------------------------------


@router.get("/lists/{list_name}")
async def get_list_entries(
    list_name: str,
    entry_id: str | None = None,
    session: LiveboxSession = Depends(get_session),
):
    params: dict = {"listName": list_name}
    if entry_id is not None:
        params["entryId"] = entry_id
    return await session.call("Firewall", "getListEntries", params)


@router.post("/lists/{list_name}/{entry_id}")
async def set_list_entry(
    list_name: str,
    entry_id: str,
    body: ListEntryCreate,
    session: LiveboxSession = Depends(get_session),
):
    params = body.model_dump(exclude_none=True)
    params["listName"] = list_name
    params["entryId"] = entry_id
    return await session.call("Firewall", "setListEntry", params)


@router.delete("/lists/{list_name}/{entry_id}")
async def delete_list_entry(
    list_name: str, entry_id: str, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Firewall", "deleteListEntry", {"listName": list_name, "entryId": entry_id}
    )
