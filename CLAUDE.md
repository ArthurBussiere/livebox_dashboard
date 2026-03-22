# Livebox Project

Full-stack Orange Livebox control UI. FastAPI backend proxies calls to the Livebox router's JSON-RPC API; Angular 21 frontend served as static files by the same backend in production.

## Architecture

```
livebox/
├── backend/        # Python FastAPI — JSON-RPC proxy for the Livebox router
├── frontend/       # Angular 21 — SSR-enabled SPA
├── Dockerfile      # Multi-stage: builds Angular then packages with Python
└── docker-compose.yml
```

In production the Angular build output (`dist/livebox_dashboard/browser/`) is copied into `backend/static/` and served by uvicorn on port 4350.

## Backend

**Stack:** Python 3.13 · FastAPI · uvicorn · httpx · Pydantic v2 · uv

```bash
cd backend
uv sync          # install dependencies
uv run uvicorn main:app --reload --port 4350   # dev server
uv run pytest    # run tests
```

**Structure:**
- `main.py` — FastAPI app, CORS, static file mount, health check
- `core/` — auth, config (pydantic-settings), session management
- `routers/` — one file per feature: auth, device, devices, dhcp, dyndns, firewall, lan, nmc, phone, system, wifi
- `models/` — Pydantic response models (one file per feature)
- `tests/` — pytest + pytest-asyncio
- `bruno/` — Bruno API collections for manual testing

**Environment variables** (via `.env` at project root):
| Variable | Description |
|---|---|
| `LIVEBOX_URL` | Router address (default: `http://192.168.1.1`) |
| `LIVEBOX_USER` | Router admin username |
| `LIVEBOX_PASSWORD` | Router admin password |
| `LIVEBOX_REQUEST_TIMEOUT` | HTTP timeout in seconds (default: 10) |
| `LIVEBOX_API_USER` | API basic-auth username |
| `LIVEBOX_API_PASSWORD` | API basic-auth password |

## Frontend

**Stack:** Angular 21 · TypeScript 5.9 · SSR (Express 5) · RxJS · Vitest · Prettier

```bash
cd frontend
npm install
npm start               # dev server on :4200 (proxies /api → :4350)
npm run build           # production build → dist/livebox_dashboard/browser/
npm test                # vitest unit tests
```

**Structure:**
- `src/app/features/` — feature modules: devices, dhcp, dyndns, firewall, lan, login, system, wifi
- `src/app/services/` — HTTP/API services
- `src/app/core/` — guards, interceptors, providers
- `src/app/shared/` — reusable components (header, toast, spinner, dialog…)
- `src/app/models/` — TypeScript types mirroring backend Pydantic models
- `proxy.conf.json` — dev proxy: `/api/*` → `http://localhost:4350`

## Docker

```bash
# Build
docker build -t livebox_dashboard .

# Run
docker run --rm -p 4350:4350 --env-file .env livebox_dashboard

# Or with Compose
docker compose up --build
```

App is available at http://localhost:4350.
