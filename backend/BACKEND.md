# Backend

FastAPI application that acts as a RESTful wrapper around the Orange Livebox JSON-RPC API (`/ws`). It handles authentication against the box, exposes typed endpoints, and serves the Angular frontend in production.

## Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| HTTP client | httpx (async) |
| Config | pydantic-settings |
| Runtime | Python 3.13, uvicorn |
| Dependency manager | uv |

## Project structure

```
backend/
├── main.py            # App factory, middleware, routers, static serving
├── core/
│   ├── config.py      # Settings loaded from .env
│   ├── session.py     # Livebox JSON-RPC session (singleton)
│   └── auth.py        # API session token store
├── routers/
│   ├── auth.py        # POST /auth/login, POST /auth/logout
│   ├── device.py
│   ├── devices.py
│   ├── dhcp.py
│   ├── dyndns.py
│   ├── firewall.py
│   ├── lan.py
│   ├── nmc.py
│   ├── phone.py
│   ├── system.py
│   └── wifi.py
├── models/            # Pydantic request/response models
├── tests/
├── pyproject.toml
└── .env
```

## Configuration

All settings are loaded from `.env` via pydantic-settings with the `LIVEBOX_` prefix.

| Env var | Default | Description |
|---|---|---|
| `LIVEBOX_URL` | `http://192.168.1.1` | Livebox IP/hostname |
| `LIVEBOX_USER` | `admin` | Livebox admin username |
| `LIVEBOX_PASSWORD` | `admin` | Livebox admin password |
| `LIVEBOX_REQUEST_TIMEOUT` | `10.0` | HTTP timeout per request (seconds) |
| `LIVEBOX_API_USER` | `admin` | Username to log in to this API |
| `LIVEBOX_API_PASSWORD` | `changeme` | Password to log in to this API |
| `LIVEBOX_SESSION_TTL` | `86400` | Session token lifetime (seconds, default 24h) |

## How it works

### 1. Livebox session (`core/session.py`)

At startup, a `LiveboxSession` singleton authenticates against the Livebox by calling the `sah.Device.Information.createContext` JSON-RPC method. The response returns a `contextID` which is sent as `Authorization: X-Sah <token>` on every subsequent request.

If a call returns HTTP 401 or a JSON payload with status `13` ("Permission denied"), the session re-authenticates automatically and retries the request once.

The session is initialised in the FastAPI lifespan and injected into routers via the `get_session()` dependency:

```python
async def list_devices(session: LiveboxSession = Depends(get_session)):
    return await session.call("Hosts", "getDevices", {})
```

### 2. API authentication (`core/auth.py`)

Protects the API from unauthenticated access using an in-memory session token store.

**Login flow:**
1. `POST /auth/login` with `{ "username": "...", "password": "..." }`
2. Credentials are checked against `LIVEBOX_API_USER` / `LIVEBOX_API_PASSWORD`
3. A `secrets.token_urlsafe(32)` token is generated and stored with an expiry timestamp
4. The token is returned to the client

**Request validation:**
Every protected endpoint receives `require_auth` as a FastAPI dependency. It reads the `Authorization: Bearer <token>` header, looks up the token in the in-memory dict, and raises `401` if missing or expired.

**Token expiry:**
Tokens expire after `LIVEBOX_SESSION_TTL` seconds (default 24h). Expired tokens are evicted on the next validation attempt.

**Logout:**
`POST /auth/logout` removes the token from the store immediately.

### 3. Route protection

All routers except `/auth` and `/health` are mounted with the `require_auth` dependency:

```python
_protected = {"dependencies": [Depends(require_auth)]}

app.include_router(auth.router,   prefix="/auth")           # public
app.include_router(wifi.router,   prefix="/wifi", **_protected)
# ...
```

### 4. Static file serving (`main.py`)

In the Docker container, the Angular build is copied to `./static/`. FastAPI mounts it at the end of the router chain:

```python
app.mount("/", StaticFiles(directory="static", html=True), name="spa")
```

`html=True` enables the SPA fallback: any path that does not match a file serves `index.html`, which lets Angular's client-side router take over. The static mount is only activated when the `static/` directory exists, so the backend works standalone during local development.

## API endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | No | Health check |
| `POST` | `/auth/login` | No | Obtain a session token |
| `POST` | `/auth/logout` | Yes | Revoke the current token |
| `*` | `/device/*` | Yes | Device info & management |
| `*` | `/devices/*` | Yes | Network devices (hosts) |
| `*` | `/wifi/*` | Yes | Wi-Fi settings |
| `*` | `/firewall/*` | Yes | Firewall rules & port forwarding |
| `*` | `/dhcp/*` | Yes | DHCP leases & pools |
| `*` | `/lan/*` | Yes | LAN interfaces & stats |
| `*` | `/dyndns/*` | Yes | Dynamic DNS |
| `*` | `/nmc/*` | Yes | Network management & WAN |
| `*` | `/phone/*` | Yes | VoIP configuration |
| `*` | `/system/*` | Yes | Diagnostics & DNS |

Interactive docs are available at `/docs` (Swagger UI) and `/redoc`.

## Running locally

```bash
# Install dependencies
uv sync

# Start the dev server (hot-reload)
uv run uvicorn main:app --reload
```

The server starts on `http://localhost:8000`. The `static/` directory is absent in local dev, so the SPA mount is skipped — use the Angular dev server (`ng serve`) instead.

## Running with Docker

From the monorepo root:

```bash
docker compose up --build
```

The multi-stage Dockerfile builds Angular first, then packages everything into a single Python image.
