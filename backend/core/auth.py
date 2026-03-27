import secrets
import time

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings
from .session import LiveboxSession

# token → (LiveboxSession, expiry timestamp)
_sessions: dict[str, tuple[LiveboxSession, float]] = {}

_bearer = HTTPBearer()


def create_token(session: LiveboxSession) -> str:
    token = secrets.token_urlsafe(32)
    _sessions[token] = (session, time.time() + settings.session_ttl)
    return token


async def revoke_token(token: str) -> None:
    entry = _sessions.pop(token, None)
    if entry:
        await entry[0].close()


def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    token = credentials.credentials
    entry = _sessions.get(token)
    if entry is None or time.time() > entry[1]:
        _sessions.pop(token, None)
        raise HTTPException(status_code=401, detail="Invalid or expired session token")
    return token


async def get_session(token: str = Depends(require_auth)) -> LiveboxSession:
    return _sessions[token][0]


def get_session_by_token(token: str) -> LiveboxSession | None:
    """Validate a raw bearer token and return its session, or None if invalid/expired."""
    entry = _sessions.get(token)
    if entry is None or time.time() > entry[1]:
        _sessions.pop(token, None)
        return None
    return entry[0]
