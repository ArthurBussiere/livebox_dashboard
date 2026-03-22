import pytest
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from core.session import get_session
from main import app


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.call = AsyncMock(return_value={"status": 0, "data": {}})
    return session


@pytest.fixture
async def client(mock_session):
    app.dependency_overrides[get_session] = lambda: mock_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


def permission_denied():
    return HTTPException(status_code=403, detail="Permission denied")


def not_found():
    return HTTPException(status_code=404, detail="Object not found")
