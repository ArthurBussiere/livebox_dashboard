from fastapi import APIRouter, Depends

from core.session import LiveboxSession
from core.auth import get_session
from models.system import (
    DiagnosticsExecuteRequest,
    DiagnosticsTriggerRequest,
    DNSRequest,
    UserInputRequest,
)

router = APIRouter()

# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


@router.get("/diagnostics")
async def list_diagnostics(session: LiveboxSession = Depends(get_session)):
    return await session.call("AutoDiag", "listDiagnostics", {})


@router.get("/diagnostics/state")
async def get_diagnostics_state(session: LiveboxSession = Depends(get_session)):
    return await session.call("AutoDiag", "getDiagnosticsState", {})


@router.post("/diagnostics/trigger")
async def execute_trigger(
    body: DiagnosticsTriggerRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call("AutoDiag", "executeTrigger", {"event": body.event})


@router.get("/diagnostics/whitelist/datamodel")
async def get_datamodel_whitelist(session: LiveboxSession = Depends(get_session)):
    return await session.call("AutoDiag", "getDatamodelWhiteList", {})


@router.get("/diagnostics/whitelist/function")
async def get_function_whitelist(session: LiveboxSession = Depends(get_session)):
    return await session.call("AutoDiag", "getFunctionWhiteList", {})


@router.get("/diagnostics/context")
async def get_context(session: LiveboxSession = Depends(get_session)):
    return await session.call("AutoDiag", "getContext", {})


@router.delete("/diagnostics/context")
async def clear_context(session: LiveboxSession = Depends(get_session)):
    return await session.call("AutoDiag", "clearContext", {})


@router.post("/diagnostics/input")
async def set_user_input(
    body: UserInputRequest, session: LiveboxSession = Depends(get_session)
):
    return await session.call("AutoDiag", "setUserInput", {"input": body.input})


@router.post("/diagnostics/{id}")
async def execute_diagnostics(
    id: str,
    body: DiagnosticsExecuteRequest | None = None,
    session: LiveboxSession = Depends(get_session),
):
    params: dict = {"id": id}
    if body and body.usr is not None:
        params["usr"] = body.usr
    return await session.call("AutoDiag", "executeDiagnostics", params)


@router.delete("/diagnostics/{id}")
async def cancel_diagnostics(
    id: str | None = None, session: LiveboxSession = Depends(get_session)
):
    params = {}
    if id is not None:
        params["id"] = id
    return await session.call("AutoDiag", "cancelDiagnostics", params)


# ---------------------------------------------------------------------------
# DNS
# ---------------------------------------------------------------------------


@router.get("/dns")
async def get_dns_servers(
    body: DNSRequest | None = None, session: LiveboxSession = Depends(get_session)
):
    params = body.model_dump(exclude_none=True) if body else {}
    return await session.call("DNS", "getDNSServers", params)
