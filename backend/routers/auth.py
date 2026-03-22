from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.auth import create_token, require_auth, revoke_token
from core.config import settings
from core.session import LiveboxSession

router = APIRouter()


class LoginRequest(BaseModel):
    url: str
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    session = LiveboxSession(body.url, body.username, body.password, settings.request_timeout)
    await session.signin()  # raises 401/502 on bad credentials or unreachable box
    return TokenResponse(token=create_token(session))


@router.get("/check", status_code=204)
async def check(_: str = Depends(require_auth)) -> None:
    """Verify the session token is still valid."""


@router.post("/logout", status_code=204)
async def logout(token: str = Depends(require_auth)) -> None:
    await revoke_token(token)
