# Frontend

Angular single-page application providing a UI for the Livebox API backend. All pages are protected by an authentication guard; unauthenticated users are redirected to the login page.

## Stack

| Layer | Technology |
|---|---|
| Framework | Angular 19 |
| Language | TypeScript |
| HTTP | Angular HttpClient |
| Auth storage | localStorage |
| Build | Angular CLI (`ng build`) |

## Project structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── app.ts             # Root component
│   │   ├── app.routes.ts      # Route definitions + guards
│   │   ├── app.config.ts      # App-level providers (HTTP, router)
│   │   ├── core/
│   │   │   ├── api.service.ts           # Generic HTTP wrapper
│   │   │   ├── auth.service.ts          # Login, logout, token storage
│   │   │   ├── auth.interceptor.ts      # Attaches Bearer token to requests
│   │   │   ├── error.interceptor.ts     # Global HTTP error handling
│   │   │   ├── notification.service.ts  # Toast notifications
│   │   │   └── layout.service.ts
│   │   ├── features/
│   │   │   ├── login/
│   │   │   ├── devices/
│   │   │   ├── wifi/
│   │   │   ├── firewall/
│   │   │   ├── dhcp/
│   │   │   ├── dyndns/
│   │   │   ├── lan/
│   │   │   └── system/
│   │   ├── services/          # Per-domain API service wrappers
│   │   ├── models/            # TypeScript interfaces matching backend models
│   │   └── shared/            # Reusable components (header, toast, dialogs...)
│   ├── environments/
│   │   ├── environment.ts           # Dev: apiUrl = 'http://localhost:8000'
│   │   └── environment.prod.ts      # Prod: apiUrl = '' (relative, same origin)
│   └── styles.css
├── proxy.conf.json    # Dev proxy: /api → http://localhost:8000
├── angular.json
└── package.json
```

## How it works

### 1. Authentication (`core/auth.service.ts`)

The `AuthService` manages the session token using an Angular signal.

**Login:**
1. The login page calls `AuthService.login(username, password)`
2. A `POST /auth/login` request is sent to the backend
3. On success, the returned token is saved in `localStorage` under the key `livebox_token` and stored in a signal
4. The user is redirected to `/devices`

**Persistence:**
The signal is initialised from `localStorage` at startup, so the session survives a page refresh without requiring a new login.

**Logout:**
`AuthService.logout()` clears the token from `localStorage` and the signal, redirects to `/login`, then fires `POST /auth/logout` in the background to revoke the server-side token.

### 2. Route guards (`app.routes.ts`)

Two inline guards control navigation:

| Guard | Behaviour |
|---|---|
| `authGuard` | Redirects to `/login` if no token is present |
| `noAuthGuard` | Redirects to `/devices` if a token is already present (prevents visiting login while authenticated) |

All feature routes use `authGuard`. The login route uses `noAuthGuard`.

### 3. HTTP interceptors (`app.config.ts`)

Two functional interceptors are registered globally in the order they are listed:

**`authInterceptor`** — runs first, clones every outgoing request and adds the `Authorization: Bearer <token>` header if a token exists.

**`errorInterceptor`** — runs on responses, handles two cases:
- `401` on any non-login request: clears the token and redirects to `/login` (expired or revoked session)
- Any other error: displays a toast notification with the error detail and re-throws for the component to handle

### 4. API communication (`core/api.service.ts`)

`ApiService` is a thin wrapper around `HttpClient` that prepends `environment.apiUrl` to every path:

```typescript
this.api.get<Device[]>('/devices')
// dev  → GET http://localhost:8000/devices
// prod → GET /devices  (same-origin, served by FastAPI)
```

Query parameters are handled via a `toParams()` helper that skips `undefined` values and supports arrays.

Each feature module has its own domain service (e.g. `WifiService`, `FirewallService`) that calls `ApiService` and maps responses to typed models.

### 5. Environment and API URL

In development, `environment.apiUrl` is `http://localhost:8000` and a proxy (`proxy.conf.json`) forwards `/api` requests to the backend — though the app calls the backend directly without the `/api` prefix.

In production (Docker container), `environment.prod.ts` sets `apiUrl` to `''`. All HTTP calls become relative URLs, which land on FastAPI running on the same origin.

## Routes

| Path | Guard | Component |
|---|---|---|
| `/` | — | Redirects to `/devices` |
| `/login` | `noAuthGuard` | Login form |
| `/devices` | `authGuard` | Network devices list |
| `/wifi` | `authGuard` | Wi-Fi settings |
| `/firewall` | `authGuard` | Firewall rules & port forwarding |
| `/dhcp` | `authGuard` | DHCP leases & static assignments |
| `/dyndns` | `authGuard` | Dynamic DNS hosts |
| `/lan` | `authGuard` | LAN interfaces & stats |
| `/system` | `authGuard` | Diagnostics |
| `/**` | — | Redirects to `/devices` |

All feature components are lazy-loaded via `loadComponent()`.

## Running locally

```bash
# Install dependencies
npm install

# Start dev server (with proxy to backend on :8000)
npm start
# → http://localhost:4200
```

The Angular dev server proxies requests so `AuthService` talks directly to `http://localhost:8000`. The backend must be running separately.

## Building for production

```bash
npm run build -- --configuration production
```

Output lands in `dist/liveboxUI/browser/`. In the Docker build, this directory is copied into the backend image at `./static/` and served by FastAPI.
