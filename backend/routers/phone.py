from fastapi import APIRouter, Depends

from core.session import LiveboxSession
from core.auth import get_session

router = APIRouter()


@router.get("/config")
async def get_voip_config(session: LiveboxSession = Depends(get_session)):
    return await session.call("NMC", "getVoIPConfig", {})


@router.get("/info")
async def get_voip_info(session: LiveboxSession = Depends(get_session)):
    return await session.call("VoiceService", "get", {})
