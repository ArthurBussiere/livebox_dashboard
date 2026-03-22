# Frontend Implementation Plan — LiveboxUI

Step-by-step guide to build the Angular 21 admin UI for the `livebox_api` FastAPI backend.

---

## Overview

The application is a **router admin dashboard** exposing all Livebox features through a clean UI. The backend runs at `http://localhost:8000` (FastAPI, no frontend auth — session with the box is managed server-side).

**Sections:**
| Section | API prefix | Description |
|---|---|---|
| Dashboard | `/lan`, `/nmc` | Overview: WAN status, connected devices count, WiFi state |
| Devices | `/devices` | Connected device list, names, types, tags |
| WiFi | `/wifi` | Enable/disable, guest network, pairing, WPS |
| Firewall | `/firewall` | Level, port forwarding, pinhole, DMZ, custom rules |
| DHCP | `/dhcp` | Leases, static leases, pools |
| DynDNS | `/dyndns` | Dynamic DNS hosts |
| System | `/nmc`, `/device`, `/system` | WAN mode, LAN IP, reboot, firmware, diagnostics, DNS |
| Phone | `/phone` | VoIP config (may return 403 on some firmware) |
| LAN Stats | `/lan` | Interface monitoring, saturation, WAN counters |

---

## Step 1 — TypeScript Models

> Reference: `MODELS.md` for full conversion rules.

Create `src/app/models/` mirroring the Python `models/` directory.

**1.1** Create `src/app/models/common.ts`:
```typescript
export interface LiveboxResponse<T = unknown> {
  status: T | null;
  data: unknown;
  errors: unknown[];
}

export interface ErrorResponse {
  detail: string;
  code?: number;
}
```

**1.2** Create one file per domain following `MODELS.md` conversion rules:
- `src/app/models/lan.ts`
- `src/app/models/dhcp.ts`
- `src/app/models/device.ts`
- `src/app/models/devices.ts`
- `src/app/models/dyndns.ts`
- `src/app/models/firewall.ts`
- `src/app/models/wifi.ts`
- `src/app/models/system.ts`
- `src/app/models/nmc.ts`

**1.3** Create barrel `src/app/models/index.ts` re-exporting all files.

---

## Step 2 — HTTP Service Layer

### 2.1 Environment config

Create `src/environments/environment.ts` and `src/environments/environment.prod.ts`:
```typescript
export const environment = {
  apiUrl: 'http://localhost:8000'
};
```

Register both files in `angular.json` under `fileReplacements` for the production build configuration.

### 2.2 Base API service

Create `src/app/core/api.service.ts` — a thin wrapper over `HttpClient` that:
- Prefixes all calls with `environment.apiUrl`
- Catches `HttpErrorResponse` and re-throws as a typed `ErrorResponse`
- Exposes `get<T>`, `post<T>`, `put<T>`, `patch<T>`, `delete<T>` methods

```typescript
// Pattern — do not add extra interceptors for auth (backend handles Livebox auth)
@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  get<T>(path: string, params?: HttpParams) { ... }
  post<T>(path: string, body: unknown) { ... }
  put<T>(path: string, body: unknown) { ... }
  patch<T>(path: string, body: unknown) { ... }
  delete<T>(path: string, params?: HttpParams) { ... }
}
```

### 2.3 Feature services

Create one service per API section under `src/app/services/`:

| Service file | Wraps |
|---|---|
| `lan.service.ts` | `/lan/*` |
| `devices.service.ts` | `/devices/*` |
| `wifi.service.ts` | `/wifi/*` |
| `firewall.service.ts` | `/firewall/*` |
| `dhcp.service.ts` | `/dhcp/*` |
| `dyndns.service.ts` | `/dyndns/*` |
| `nmc.service.ts` | `/nmc/*` |
| `device.service.ts` | `/device/*` |
| `system.service.ts` | `/system/*` |
| `phone.service.ts` | `/phone/*` |

Each service is `@Injectable({ providedIn: 'root' })` and injects `ApiService`. Methods return `Observable<T>`.

**Example — `wifi.service.ts`:**
```typescript
getWifi()                    → GET  /wifi
setWifi(body: WifiConfig)    → PUT  /wifi
setEnable(body: WifiEnableRequest) → PATCH /wifi/enable
toggleEnable(body?)          → POST /wifi/enable/toggle
getGuest()                   → GET  /wifi/guest
setGuest(body: GuestConfig)  → PUT  /wifi/guest
getStats()                   → GET  /wifi/stats
startPairing(body)           → POST /wifi/pairing/start
stopPairing()                → POST /wifi/pairing/stop
```

### 2.4 Register HttpClient

In `src/app/app.config.ts`, add `provideHttpClient(withFetch())` to the providers array.

---

## Step 3 — Routing Structure

Define all routes in `src/app/app.routes.ts` using **lazy-loaded** feature components:

```typescript
export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard',  loadComponent: () => import('./features/dashboard/dashboard') },
  { path: 'devices',    loadComponent: () => import('./features/devices/devices') },
  { path: 'wifi',       loadComponent: () => import('./features/wifi/wifi') },
  { path: 'firewall',   loadComponent: () => import('./features/firewall/firewall') },
  { path: 'dhcp',       loadComponent: () => import('./features/dhcp/dhcp') },
  { path: 'dyndns',     loadComponent: () => import('./features/dyndns/dyndns') },
  { path: 'system',     loadComponent: () => import('./features/system/system') },
  { path: 'phone',      loadComponent: () => import('./features/phone/phone') },
  { path: 'lan',        loadComponent: () => import('./features/lan/lan') },
  { path: '**',         redirectTo: 'dashboard' },
];
```

Update `src/app/app.routes.server.ts` — mark all routes as `RenderMode.Client` since the pages require live API calls:

```typescript
import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  { path: '**', renderMode: RenderMode.Client }
];
```

---

## Step 4 — Shell Layout

### 4.1 App shell component

Update `src/app/app.html` to include the navigation sidebar and a `<router-outlet>`:

```html
<nav class="sidebar">
  <a routerLink="/dashboard"  routerLinkActive="active">Dashboard</a>
  <a routerLink="/devices"    routerLinkActive="active">Devices</a>
  <a routerLink="/wifi"       routerLinkActive="active">WiFi</a>
  <a routerLink="/firewall"   routerLinkActive="active">Firewall</a>
  <a routerLink="/dhcp"       routerLinkActive="active">DHCP</a>
  <a routerLink="/dyndns"     routerLinkActive="active">DynDNS</a>
  <a routerLink="/system"     routerLinkActive="active">System</a>
  <a routerLink="/phone"      routerLinkActive="active">Phone</a>
  <a routerLink="/lan"        routerLinkActive="active">LAN Stats</a>
</nav>

<main>
  <router-outlet />
</main>
```

Update `src/app/app.ts` imports to include `RouterOutlet`, `RouterLink`, `RouterLinkActive`.

### 4.2 Global error notification

Create `src/app/core/notification.service.ts` — a signal-based service that holds a queue of toast messages (error/success). Expose `error(msg)` and `success(msg)` methods. Feature services call `notificationService.error(err.detail)` in their error handlers.

---

## Step 5 — Feature Implementation

For each feature, create a directory under `src/app/features/<name>/`. Each feature is a **standalone component** that injects its service and manages state with signals.

### State pattern (use this consistently):

```typescript
// In every feature component
readonly items = signal<Item[]>([]);
readonly loading = signal(false);
readonly error = signal<string | null>(null);

ngOnInit() { this.load(); }

load() {
  this.loading.set(true);
  this.service.getItems().subscribe({
    next: data => { this.items.set(data); this.loading.set(false); },
    error: err  => { this.error.set(err.detail); this.loading.set(false); }
  });
}
```

---

### Step 5.1 — Dashboard (`/dashboard`)

**Data to load in parallel (`forkJoin`):**
- `LanService.getStatus()` → WAN status, connection type
- `LanService.getDevicesStatus()` → count of active devices
- `WifiService.getWifi()` → WiFi enabled state
- `NmcService.getWANStatus()` → WAN mode, IP, upstream/downstream

**Display:**
- WAN connection card (status, IP, mode)
- Connected devices count card
- WiFi enabled/disabled toggle (calls `WifiService.toggleEnable()`)
- Quick-action buttons: Reboot (`POST /nmc/reboot`), Check firmware (`GET /nmc/firmware/check`)

---

### Step 5.2 — Devices (`/devices`)

**Endpoints used:**
- `GET /devices` — list all devices (query param `expression`, `flags`)
- `PUT /devices/{key}/name` — rename device
- `PUT /devices/{key}/type` — change device type
- `DELETE /devices/{key}` — remove device

**UI:**
- Filterable/searchable table of devices (name, IP, MAC, type, active status)
- Inline edit for device name (click → input → save)
- Dropdown to change device type
- Delete button with confirmation dialog

---

### Step 5.3 — WiFi (`/wifi`)

**Endpoints used:**
- `GET /wifi`, `PUT /wifi` — main config
- `PATCH /wifi/enable` / `POST /wifi/enable/toggle`
- `GET /wifi/stats`
- `GET /wifi/guest`, `PUT /wifi/guest`
- `POST /wifi/pairing/start`, `POST /wifi/pairing/stop`
- `POST /wifi/wps/pin`

**UI:**
- Main WiFi card with enable toggle and config form (`WifiConfig`)
- Guest network card with enable toggle
- Stats card (current usage)
- WPS pairing section: "Start Pairing" button → shows spinner while pairing active → "Stop"
- Generate WPS PIN button

---

### Step 5.4 — Firewall (`/firewall`)

This is the most complex feature. Use a **tabbed layout** with one tab per sub-section.

**Tab: Level**
- Dropdown for IPv4 level: `Low | Medium | High | Custom` → `PUT /firewall/level`
- Same for IPv6 level → `PUT /firewall/ipv6-level`
- Ping response toggles per interface → `PUT /firewall/ping/{interface}`
- "Commit" button → `POST /firewall/commit`

**Tab: Port Forwarding**
- Table of rules from `GET /firewall/port-forwarding`
- "Add" button → form using `PortForwardingCreate` fields
- Toggle enable per rule → `PATCH /firewall/port-forwarding/{id}/enable`
- Edit → `PUT /firewall/port-forwarding/{id}`
- Delete → `DELETE /firewall/port-forwarding/{id}`

**Tab: DMZ**
- Table from `GET /firewall/dmz`
- Add/delete form using `DMZCreate`

**Tab: Pinhole (IPv6)**
- Table from `GET /firewall/pinhole`
- Add using `PinholeCreate`, delete with origin param

**Tab: Custom Rules**
- Table from `GET /firewall/custom-rules`
- Add using `CustomRuleCreate`
- Filter by chain (query param)

**Tab: Protocol Forwarding**
- Table from `GET /firewall/protocol-forwarding`
- Add using `ProtocolForwardingCreate`

---

### Step 5.5 — DHCP (`/dhcp`)

**Tabbed layout:**

**Tab: Active Leases**
- Table from `GET /dhcp/leases`
- "Promote to static" action for each lease row

**Tab: Static Leases**
- Table from `GET /dhcp/leases/static`
- Add form: MAC + IP → `POST /dhcp/leases/static`
- Edit IP or enable/disable → `PUT /dhcp/leases/static/{mac}`
- Delete → `DELETE /dhcp/leases/static/{mac}`
- Force renew → `POST /dhcp/leases/static/{mac}/renew`

**Tab: Settings**
- Lease time input → `PUT /dhcp/lease-time`
- DORA cycle stats card from `GET /dhcp/stats/dora`

---

### Step 5.6 — DynDNS (`/dyndns`)

**UI:**
- Global enable toggle → `PATCH /dyndns/enable`
- CGNAT enable toggle → `PATCH /dyndns/cgnat`
- Table of hosts from `GET /dyndns`
- "Add host" form using `DynDNSHostCreate`:
  - Service dropdown populated from `GET /dyndns/services`
  - Hostname, username, password inputs
  - Enable checkbox (default: true)
- Delete host → `DELETE /dyndns/{hostname}`

---

### Step 5.7 — System (`/system` + `/nmc` + `/device`)

**Tabbed layout:**

**Tab: WAN**
- WAN status card from `GET /nmc/wan/status`
- Change WAN mode: dropdown from `GET /nmc/wan/modes` + credentials form → `PUT /nmc/wan/mode`

**Tab: LAN**
- LAN IP config form from `GET /nmc/lan-ip` → `PUT /nmc/lan-ip`
- Fields: address, netmask, DHCP enable toggle, DHCP range (min/max), lease time

**Tab: IPv6**
- IPv6 config form from `GET /nmc/ipv6` → `PUT /nmc/ipv6`
- Enable toggle + optional user-requested booleans

**Tab: Remote Access**
- List remote access entries from `GET /nmc/remote-access`
- Add form using `RemoteAccessCreate`
- Disable by access type → `DELETE /nmc/remote-access`

**Tab: Device**
- Device info card from `GET /device/info`
- Firmware section: version info + "Check for upgrades" button → `GET /nmc/firmware/check`
- Config export: filename input → `POST /device/export`
- Config restore form using `RestoreRequest`

**Tab: Diagnostics**
- List diagnostics from `GET /system/diagnostics`
- Run a diagnostic: select from list → `POST /system/diagnostics/{id}`
- Cancel → `DELETE /system/diagnostics/{id}`
- State polling via `GET /system/diagnostics/state`
- DNS servers display from `GET /system/dns`

**Tab: System Control**
- Reboot button → `POST /nmc/reboot` (confirm dialog first)
- Reset button → `POST /nmc/reset` (confirm dialog first)
- LED controls from `GET /nmc/led/{name}` → `PUT /nmc/led/{name}`

---

### Step 5.8 — Phone (`/phone`)

**UI:**
- VoIP config card from `GET /phone/config`
- VoIP info card from `GET /phone/info`
- Display a warning banner if the API returns 403 (restricted on some firmware)

---

### Step 5.9 — LAN Stats (`/lan`)

**UI:**
- WAN counters card from `GET /lan/wan-counters`
- Interfaces list from `GET /lan/interfaces`
- Device names list from `GET /lan/devices`
- Saturation results from `GET /lan/saturation`
- **Interface monitoring:**
  - Form: duration + interval → `POST /lan/monitoring/interface/start`
  - "Stop" → `POST /lan/monitoring/interface/stop`
- **LAN stats chart:**
  - Form: seconds, number of readings, interface names (multi-select) → `GET /lan/stats`
  - Display results as a simple table or chart

---

## Step 6 — Shared UI Components

Create reusable components under `src/app/shared/`:

| Component | Purpose |
|---|---|
| `confirm-dialog` | Reusable confirm modal (reboot, delete) |
| `loading-spinner` | Overlay or inline spinner |
| `error-banner` | Dismissable error alert |
| `data-table` | Generic table with sort/filter |
| `toggle` | Styled boolean toggle switch |
| `status-badge` | Colored pill for active/inactive states |

These are **standalone components** imported directly where needed.

---

## Step 7 — Error Handling

### 7.1 HTTP interceptor

Create `src/app/core/error.interceptor.ts` as a functional interceptor:

```typescript
export const errorInterceptor: HttpInterceptorFn = (req, next) =>
  next(req).pipe(
    catchError((err: HttpErrorResponse) => {
      const message = err.error?.detail ?? err.message;
      inject(NotificationService).error(message);
      return throwError(() => err.error as ErrorResponse);
    })
  );
```

Register in `app.config.ts` with `provideHttpClient(withFetch(), withInterceptors([errorInterceptor]))`.

### 7.2 Global error listener

`provideBrowserGlobalErrorListeners()` is already in `app.config.ts` — it will catch unhandled promise rejections.

---

## Step 8 — SSR Considerations

All pages perform live API calls at render time and must **not** run on the server. This is already handled by `RenderMode.Client` set in Step 3.

If you need SEO-friendly meta tags on any page (unlikely for a router admin), use Angular's `Meta` and `Title` services — they work with SSR hydration.

Do **not** use `localStorage`, `window`, or `document` directly — wrap in `isPlatformBrowser()` or use Angular's `PLATFORM_ID` injection if ever needed outside client-only routes.

---

## Step 9 — Styling

No CSS framework is prescribed. Apply styles in `src/styles.css` (global) and per-component `.css` files.

Suggested approach:
- CSS custom properties for the color palette (one dark sidebar, one light content area)
- CSS Grid for the dashboard card layout
- CSS Flexbox for forms and tables
- No third-party UI library dependency — keeps the bundle small

---

## Implementation Order (Recommended)

1. Models (`Step 1`) + `ApiService` (`Step 2.1–2.2`)
2. Feature services (`Step 2.3–2.4`)
3. Routing + Shell layout (`Step 3–4`)
4. Error interceptor + Notification service (`Step 7`)
5. Shared UI components (`Step 6`)
6. Dashboard (`Step 5.1`) — validates the full stack end-to-end
7. Devices → WiFi → DHCP → DynDNS (simpler CRUD features)
8. Firewall (most complex, do last in the CRUD group)
9. System tabs
10. LAN Stats + Phone
