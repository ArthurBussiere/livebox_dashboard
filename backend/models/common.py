from typing import Any

from pydantic import BaseModel


class LiveboxResponse(BaseModel):
    status: Any = None
    data: Any = None
    errors: list[Any] = []


class ErrorResponse(BaseModel):
    detail: str
    code: int | None = None
