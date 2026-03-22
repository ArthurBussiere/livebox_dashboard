import logging

from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from core.auth import require_auth
from routers import auth, device, dhcp, devices, dyndns, firewall, lan, nmc, phone, system, wifi

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Livebox API",
    description="RESTful CRUD wrapper for the Orange Livebox JSON-RPC API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # dev only
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.status_code},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Request validation error",
            "code": 422,
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "code": 500},
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Health"])
async def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

_protected = {"dependencies": [Depends(require_auth)]}

app.include_router(auth.router,     prefix="/api/auth",     tags=["Auth"])
app.include_router(device.router,   prefix="/api/device",   tags=["Device"],   **_protected)
app.include_router(firewall.router, prefix="/api/firewall", tags=["Firewall"], **_protected)
app.include_router(lan.router,      prefix="/api/lan",      tags=["LAN"],      **_protected)
app.include_router(wifi.router,     prefix="/api/wifi",     tags=["WiFi"],     **_protected)
app.include_router(phone.router,    prefix="/api/phone",    tags=["Phone"],    **_protected)
app.include_router(dyndns.router,   prefix="/api/dyndns",   tags=["DynDNS"],   **_protected)
app.include_router(nmc.router,      prefix="/api/nmc",      tags=["NMC"],      **_protected)
app.include_router(dhcp.router,     prefix="/api/dhcp",     tags=["DHCP"],     **_protected)
app.include_router(devices.router,  prefix="/api/devices",  tags=["Devices"],  **_protected)
app.include_router(system.router,   prefix="/api/system",   tags=["System"],   **_protected)


# ---------------------------------------------------------------------------
# Static files (Angular build) — must come after all API routers
# ---------------------------------------------------------------------------

_STATIC = Path(__file__).parent / "static"


@app.get("/{full_path:path}", include_in_schema=False)
async def spa(full_path: str) -> FileResponse:
    file = _STATIC / full_path
    if file.is_file():
        return FileResponse(file)
    index = _STATIC / "index.html"
    if index.is_file():
        return FileResponse(index)
    raise HTTPException(status_code=404, detail="Not found")
