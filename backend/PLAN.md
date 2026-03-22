# Livebox FastAPI CRUD — Implementation Plan

**Source reference:** https://github.com/p-dor/LiveboxMonitor/tree/main/docs

---

## Overview

Translate the Livebox JSON-RPC API into a RESTful FastAPI application using Pydantic v2.
Every JSON-RPC call becomes a standard HTTP verb (`GET` / `POST` / `PUT` / `DELETE` / `PATCH`).
A single `LmSession` wrapper handles authentication and forwards calls to the box.

---

## Step-by-step plan

### Step 1 — uv project boilerplate ✅

Initialize the project with `uv`, create the package skeleton, and verify the app boots.

```bash
uv init --no-readme
uv add fastapi "uvicorn[standard]" "pydantic>=2.7" "pydantic-settings>=2.2" httpx python-dotenv
uv add --dev pytest pytest-asyncio pytest-cov
```

**Files created:**

```
livebox_api/
├── main.py              # FastAPI app + /health endpoint
├── core/
│   └── __init__.py
├── models/
│   └── __init__.py
├── routers/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml       # uv-managed, includes [tool.pytest.ini_options]
├── uv.lock
├── .env.example
└── .gitignore
```

**Smoke test:** `uv run uvicorn main:app --reload` → `GET /health` returns `{"status": "ok"}`.

**Run commands:**

```bash
uv run uvicorn main:app --reload          # dev server
uv run pytest                             # tests
uv run pytest --cov=. --cov-report=html   # coverage
```

---

### Step 2 — Full project layout (target state)

All files to be created in subsequent steps:

```
livebox_api/
├── main.py              ✅ done
├── core/
│   ├── __init__.py      ✅ done
│   ├── config.py        # settings (Livebox URL, credentials via env)
│   └── session.py       # LmSession wrapper (singleton / per-request)
├── models/
│   ├── __init__.py      ✅ done
│   ├── common.py        # shared base models, error envelope
│   ├── device.py
│   ├── firewall.py
│   ├── lan.py
│   ├── wifi.py
│   ├── phone.py
│   ├── dyndns.py
│   ├── nmc.py
│   ├── dhcp.py
│   ├── devices.py
│   └── system.py
├── routers/
│   ├── __init__.py      ✅ done
│   ├── device.py
│   ├── firewall.py
│   ├── lan.py
│   ├── wifi.py
│   ├── phone.py
│   ├── dyndns.py
│   ├── nmc.py
│   ├── dhcp.py
│   ├── devices.py
│   └── system.py
├── tests/
│   ├── __init__.py      ✅ done
│   └── test_*.py        # one per router
├── pyproject.toml       ✅ done
├── uv.lock              ✅ done
├── .env.example         ✅ done
└── .gitignore           ✅ done
```

---

### Step 3 — Core session layer (`core/session.py`) ✅

The Livebox API is JSON-RPC over HTTP POST.
Every call has the form:

```json
POST http://<box_ip>/ws
Content-Type: application/x-sah-ws-4-call+json
Authorization: X-Sah <token>

{
  "service": "NMC",
  "method": "get",
  "parameters": {}
}
```

Implement:

- `LiveboxSession` — async context manager that authenticates on enter, calls `signIn`, stores the session cookie / token.
- `call(service, method, parameters)` → raw dict response.
- FastAPI dependency `get_session()` — returns a cached `LiveboxSession` (one per app lifetime, re-auth on 401).
- Settings read from environment: `LIVEBOX_URL`, `LIVEBOX_USER`, `LIVEBOX_PASSWORD`.

---

### Step 4 — Common models (`models/common.py`)

```python
from pydantic import BaseModel
from typing import Any

class LiveboxResponse(BaseModel):
    status: Any = None
    errors: list[str] = []

class ErrorResponse(BaseModel):
    detail: str
    code: int | None = None
```

All router responses are `LiveboxResponse` or domain-specific subclasses.

---

### Step 5 — Module: Device Info (`routers/device.py`)

**JSON-RPC service:** `DeviceInfo`

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/device/info` | GET | `DeviceInfo.get` |
| `/device/pairing` | GET | `DeviceInfo.getPairingInfo` |
| `/device` | PUT | `DeviceInfo.update` |
| `/device/export` | POST | `DeviceInfo.export` |
| `/device/config/restore` | POST | `DeviceInfo.VendorConfigFile.Restore` |
| `/device/config/restore-extended` | POST | `DeviceInfo.VendorConfigFile.RestoreExtended` |

**Pydantic models:**

```python
class ExportRequest(BaseModel):
    file_name: str

class RestoreRequest(BaseModel):
    url: str
    username: str
    password: str
    file_size: int | None = None
    target_file_name: str | None = None
    checksum_algorithm: str | None = None
    checksum: str | None = None
```

---

### Step 6 — Module: Firewall (`routers/firewall.py`)

**JSON-RPC service:** `Firewall`

#### Firewall level

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/firewall/level` | GET | `Firewall.getFirewallLevel` |
| `/firewall/level` | PUT | `Firewall.setFirewallLevel` |
| `/firewall/ipv6-level` | GET | `Firewall.getFirewallIPv6Level` |
| `/firewall/ipv6-level` | PUT | `Firewall.setFirewallIPv6Level` |
| `/firewall/commit` | POST | `Firewall.commit` |
| `/firewall/ping/{interface}` | GET | `Firewall.getRespondToPing` |
| `/firewall/ping/{interface}` | PUT | `Firewall.setRespondToPing` |

#### Port Forwarding

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/firewall/port-forwarding` | GET | `Firewall.getPortForwarding` |
| `/firewall/port-forwarding` | POST | `Firewall.setPortForwarding` (create) |
| `/firewall/port-forwarding/{id}` | PUT | `Firewall.setPortForwarding` (update) |
| `/firewall/port-forwarding/{id}` | DELETE | `Firewall.deletePortForwarding` |
| `/firewall/port-forwarding/{id}/enable` | PATCH | `Firewall.enablePortForwarding` |
| `/firewall/port-forwarding/{id}/refresh` | POST | `Firewall.refreshPortForwarding` |

#### Protocol Forwarding

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/firewall/protocol-forwarding` | GET | `Firewall.getProtocolForwarding` |
| `/firewall/protocol-forwarding` | POST | `Firewall.setProtocolForwarding` |
| `/firewall/protocol-forwarding/{id}` | DELETE | `Firewall.deleteProtocolForwarding` |

#### Pinhole (IPv6)

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/firewall/pinhole` | GET | `Firewall.getPinhole` |
| `/firewall/pinhole` | POST | `Firewall.setPinhole` |
| `/firewall/pinhole/{id}` | DELETE | `Firewall.deletePinhole` |

#### DMZ

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/firewall/dmz` | GET | `Firewall.getDMZ` |
| `/firewall/dmz` | POST | `Firewall.setDMZ` |
| `/firewall/dmz/{id}` | DELETE | `Firewall.deleteDMZ` |

#### Custom Rules

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/firewall/custom-rules` | GET | `Firewall.getCustomRule` |
| `/firewall/custom-rules` | POST | `Firewall.setCustomRule` |
| `/firewall/custom-rules/{id}` | DELETE | `Firewall.deleteCustomRule` |

#### Redirect

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/firewall/redirect` | GET | `Firewall.getRedirect` |
| `/firewall/redirect` | POST | `Firewall.setRedirect` |
| `/firewall/redirect/{id}` | DELETE | `Firewall.deleteRedirect` |

#### List Entries

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/firewall/lists/{list_name}` | GET | `Firewall.getListEntries` |
| `/firewall/lists/{list_name}/{entry_id}` | POST | `Firewall.setListEntry` |
| `/firewall/lists/{list_name}/{entry_id}` | DELETE | `Firewall.deleteListEntry` |

**Key Pydantic models:**

```python
class FirewallLevel(BaseModel):
    level: str  # "Low" | "Medium" | "High" | "Custom"

class PortForwardingCreate(BaseModel):
    origin: str
    source_interface: str
    internal_port: int
    destination_ip_address: str
    protocol: str  # "TCP" | "UDP" | "TCP,UDP"
    external_port: int | None = None
    source_prefix: str | None = None
    enable: bool = True
    persistent: bool = True
    description: str | None = None
    destination_mac_address: str | None = None
    lease_duration: int | None = None

class PortForwardingEnableRequest(BaseModel):
    enable: bool

class PinholeCreate(BaseModel):
    origin: str
    source_interface: str
    destination_port: int
    destination_ip_address: str
    protocol: str
    source_port: int | None = None
    source_prefix: str | None = None
    ip_version: int | None = None
    enable: bool = True
    persistent: bool = True
    description: str | None = None

class DMZCreate(BaseModel):
    source_interface: str
    destination_ip_address: str
    enable: bool
    source_prefix: str | None = None

class CustomRuleCreate(BaseModel):
    chain: str | None = None
    action: str
    destination_port: str | None = None
    source_port: str | None = None
    destination_prefix: str | None = None
    source_prefix: str | None = None
    protocol: str | None = None
    ip_version: int | None = None
    enable: bool = True
    description: str | None = None
    persistent: bool = True
```

---

### Step 7 — Module: LAN / HomeLan (`routers/lan.py`)

**JSON-RPC service:** `HomeLan`

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/lan/status` | GET | `HomeLan.getStatus` |
| `/lan/interfaces` | GET | `HomeLan.getInterfacesNames` |
| `/lan/devices` | GET | `HomeLan.getDevicesNames` |
| `/lan/devices/status` | GET | `HomeLan.getDevicesStatus` |
| `/lan/wan-counters` | GET | `HomeLan.getWANCounters` |
| `/lan/saturation` | GET | `HomeLan.getSaturationResults` |
| `/lan/saturation/measures` | GET | `HomeLan.getSaturationMeasures` |
| `/lan/stats` | GET | `HomeLan.getResults` |
| `/lan/stats/device` | GET | `HomeLan.getDeviceResults` |
| `/lan/devices/{mac}` | POST | `HomeLan.addDevice` |
| `/lan/devices/{mac}` | DELETE | `HomeLan.deleteDevice` |
| `/lan/monitoring/interface/start` | POST | `HomeLan.startInterfaceMonitoringTest` |
| `/lan/monitoring/interface/stop` | POST | `HomeLan.stopInterfaceMonitoringTest` |
| `/lan/monitoring/device/start` | POST | `HomeLan.startDeviceMonitoringTest` |
| `/lan/monitoring/device/stop` | POST | `HomeLan.stopDeviceMonitoringTest` |
| `/lan/config/export` | GET | `HomeLan.export` |
| `/lan/config/import` | POST | `HomeLan.import` |

**Key Pydantic models:**

```python
class LanStatsRequest(BaseModel):
    seconds: int
    number_of_readings: int
    interface_names: list[str]
    begin_timestamp: int | None = None
    end_timestamp: int | None = None

class MonitoringTestRequest(BaseModel):
    duration: int
    interval: int
```

---

### Step 8 — Module: WiFi (`routers/wifi.py`)

**JSON-RPC service:** `NMC.Wifi`

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/wifi` | GET | `NMC.Wifi.get` |
| `/wifi` | PUT | `NMC.Wifi.set` |
| `/wifi/enable` | PATCH | `NMC.Wifi.setEnable` |
| `/wifi/enable/toggle` | POST | `NMC.Wifi.toggleEnable` |
| `/wifi/status` | PATCH | `NMC.Wifi.setStatus` |
| `/wifi/stats` | GET | `NMC.Wifi.getStats` |
| `/wifi/channel/auto` | POST | `NMC.Wifi.startAutoChannelSelection` |
| `/wifi/pairing/start` | POST | `NMC.Wifi.startPairing` |
| `/wifi/pairing/stop` | POST | `NMC.Wifi.stopPairing` |
| `/wifi/wps/pin` | POST | `NMC.Wifi.WPS.generateSelfPIN` |
| `/wifi/guest` | GET | `NMC.Guest.get` |
| `/wifi/guest` | PUT | `NMC.Guest.set` |

**Key Pydantic models:**

```python
class WifiConfig(BaseModel):
    enable: bool
    status: bool | None = None
    configuration_mode: str | None = None
    trigger_auto_channel_selection: bool | None = None

class WifiEnableRequest(BaseModel):
    value: bool
    temporary: bool | None = None
    source: str | None = None

class WifiPairingRequest(BaseModel):
    client_pin: str

class GuestConfig(BaseModel):
    enable: bool
```

---

### Step 9 — Module: Phone / VoIP (`routers/phone.py`)

**JSON-RPC service:** `VoiceService` / `Audiphone`

> Note: access is restricted on many boxes; endpoints return 403 if not available.

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/phone/config` | GET | `NMC.getVoIPConfig` |
| `/phone/info` | GET | `VoiceService.get` |

---

### Step 10 — Module: DynDNS (`routers/dyndns.py`)

**JSON-RPC service:** `DynDNS`

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/dyndns` | GET | `DynDNS.getHosts` |
| `/dyndns` | POST | `DynDNS.addHost` |
| `/dyndns/{hostname}` | DELETE | `DynDNS.delHost` |
| `/dyndns/services` | GET | `DynDNS.getServices` |
| `/dyndns/enable` | GET | `DynDNS.getGlobalEnable` |
| `/dyndns/enable` | PATCH | `DynDNS.setGlobalEnable` |
| `/dyndns/cgnat` | GET | `DynDNS.getEnableOnCgnat` |
| `/dyndns/cgnat` | PATCH | `DynDNS.setEnableOnCgnat` |

**Key Pydantic models:**

```python
class DynDNSHostCreate(BaseModel):
    service: str
    hostname: str
    username: str
    password: str
    enable: bool = True

class DynDNSEnableRequest(BaseModel):
    enable: bool
```

---

### Step 11 — Module: NMC / System (`routers/nmc.py`)

**JSON-RPC service:** `NMC`

#### Core config

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/nmc` | GET | `NMC.get` |
| `/nmc` | PUT | `NMC.set` |

#### System control

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/nmc/reboot` | POST | `NMC.reboot` |
| `/nmc/reset` | POST | `NMC.reset` |
| `/nmc/shutdown` | POST | `NMC.shutdown` |

#### WAN

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/nmc/wan/status` | GET | `NMC.getWANStatus` |
| `/nmc/wan/modes` | GET | `NMC.getWanModeList` |
| `/nmc/wan/mode` | PUT | `NMC.setWanMode` |

#### LAN IP

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/nmc/lan-ip` | GET | `NMC.getLANIP` |
| `/nmc/lan-ip` | PUT | `NMC.setLANIP` |

#### Remote access

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/nmc/remote-access` | GET | `NMC.getRemoteAccess` |
| `/nmc/remote-access` | POST | `NMC.enableRemoteAccess` |
| `/nmc/remote-access` | DELETE | `NMC.disableRemoteAccess` |

#### Firmware

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/nmc/firmware/version` | POST | `NMC.updateVersionInfo` |
| `/nmc/firmware/check` | GET | `NMC.checkForUpgrades` |

#### IPv6

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/nmc/ipv6` | GET | `NMC.IPv6.get` |
| `/nmc/ipv6` | PUT | `NMC.IPv6.set` |

#### IPTV

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/nmc/iptv/config` | GET | `NMC.OrangeTV.getIPTVConfig` |
| `/nmc/iptv/status` | GET | `NMC.OrangeTV.getIPTVStatus` |
| `/nmc/iptv/multiscreen` | GET | `NMC.OrangeTV.getIPTVMultiScreens` |
| `/nmc/iptv/multiscreen` | PUT | `NMC.OrangeTV.setIPTVMultiScreens` |

#### LED

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/nmc/led/{name}` | GET | `NMC.LED.getLedStatus` |
| `/nmc/led/{name}` | PUT | `NMC.LED.setLed` |

#### Container network

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/nmc/container` | GET | `NMC.Container.get` |
| `/nmc/container` | PUT | `NMC.Container.set` |

#### Network backup

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/nmc/network-config` | GET | `NMC.NetworkConfig.get` |
| `/nmc/network-config/backup` | POST | `NMC.NetworkConfig.launchNetworkBackup` |
| `/nmc/network-config/restore` | POST | `NMC.NetworkConfig.launchNetworkRestore` |
| `/nmc/network-config/bridge` | PATCH | `NMC.NetworkConfig.enableNetworkBR` |

#### WiFi timer

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/nmc/wlan-timer/{interface}` | GET | `NMC.WlanTimer.getActivationTimer` |
| `/nmc/wlan-timer/{interface}` | PUT | `NMC.WlanTimer.setActivationTimer` |
| `/nmc/wlan-timer/{interface}` | DELETE | `NMC.WlanTimer.disableActivationTimer` |

**Key Pydantic models:**

```python
class RebootRequest(BaseModel):
    reason: str = "User request"

class WanModeRequest(BaseModel):
    wan_mode: str
    username: str
    password: str

class LanIPConfig(BaseModel):
    address: str
    netmask: str
    dhcp_enable: bool
    dhcp_min_address: str
    dhcp_max_address: str
    lease_time: int

class RemoteAccessCreate(BaseModel):
    username: str
    password: str
    port: int
    timeout: int
    source_prefix: str
    access_type: str
    secure: bool

class IPv6Config(BaseModel):
    enable: bool
    user_requested: bool | None = None
    ipv4_user_requested: bool | None = None

class LedConfig(BaseModel):
    state: str
    color: str

class WlanTimerRequest(BaseModel):
    timeout: int
```

---

### Step 12 — Module: DHCP (`routers/dhcp.py`)

**JSON-RPC service:** `DHCPv4`

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/dhcp/leases` | GET | `DHCPv4.Server.Pool.default.getLeases` |
| `/dhcp/leases/static` | GET | `DHCPv4.Server.Pool.default.getStaticLeases` |
| `/dhcp/leases/static` | POST | `DHCPv4.Server.Pool.default.addStaticLease` |
| `/dhcp/leases/static/{mac}` | PUT | `DHCPv4.Server.Pool.default.setStaticLease` |
| `/dhcp/leases/static/{mac}` | DELETE | `DHCPv4.Server.Pool.default.deleteStaticLease` |
| `/dhcp/leases/static/{mac}/renew` | POST | `DHCPv4.Server.Pool.default.Rule.Lease.forceRenew` |
| `/dhcp/leases/pool-assign` | POST | `DHCPv4.Server.Pool.default.addLeaseFromPool` |
| `/dhcp/lease-time` | PUT | `DHCPv4.Server.Pool.default.setLeaseTime` |
| `/dhcp/pool/{id}` | GET | `DHCPv4.Server.getDHCPServerPool` |
| `/dhcp/pool` | POST | `DHCPv4.Server.createPool` |
| `/dhcp/stats` | DELETE | `DHCPv4.Server.clearStatistics` |
| `/dhcp/stats/dora` | GET | `DHCPv4.Server.Stats.getDoraCyclesDetails` |

**Key Pydantic models:**

```python
class StaticLeaseCreate(BaseModel):
    mac_address: str
    ip_address: str

class StaticLeaseUpdate(BaseModel):
    ip_address: str | None = None
    enable: bool | None = None

class LeaseTimeRequest(BaseModel):
    lease_time: int

class PoolCreate(BaseModel):
    name: str
    interface: str
```

---

### Step 13 — Module: Devices (`routers/devices.py`)

**JSON-RPC service:** `Devices`

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/devices` | GET | `Devices.get` |
| `/devices/find` | POST | `Devices.find` |
| `/devices/by-ip` | GET | `Devices.findByIPAddress` |
| `/devices/{key}` | GET | `Devices.fetchDevice` |
| `/devices/{key}` | PUT | `Devices.Device.set` |
| `/devices/{key}` | DELETE | `Devices.destroyDevice` |
| `/devices/{key}/name` | PUT | `Devices.Device.setName` |
| `/devices/{key}/name` | POST | `Devices.Device.addName` |
| `/devices/{key}/name` | DELETE | `Devices.Device.removeName` |
| `/devices/{key}/type` | PUT | `Devices.Device.setType` |
| `/devices/{key}/type` | DELETE | `Devices.Device.removeType` |
| `/devices/{key}/tags/{tag}` | GET | `Devices.Device.hasTag` |
| `/devices/{key}/tags/{tag}` | PUT | `Devices.Device.setTag` |
| `/devices/{key}/tags/{tag}` | DELETE | `Devices.Device.clearTag` |
| `/devices/{key}/topology` | GET | `Devices.Device.topology` |
| `/devices/{key}/parameters` | GET | `Devices.Device.getParameters` |
| `/devices/{key}/alternative` | PUT | `Devices.Device.setAlternative` |
| `/devices/{key}/alternative` | DELETE | `Devices.Device.removeAlternative` |

**Key Pydantic models:**

```python
class DeviceFind(BaseModel):
    expression: dict | str
    flags: str = ""

class DeviceSetName(BaseModel):
    name: str
    source: str

class DeviceSetType(BaseModel):
    type: str
    source: str

class DeviceTagRequest(BaseModel):
    expression: str = ""
    traverse: str = ""

class DeviceAlternativeRequest(BaseModel):
    alternative: str
```

---

### Step 14 — Module: System diagnostics (`routers/system.py`)

**JSON-RPC service:** `AutoDiag`

| REST endpoint | Method | JSON-RPC method |
|---|---|---|
| `/system/diagnostics` | GET | `AutoDiag.listDiagnostics` |
| `/system/diagnostics/{id}` | POST | `AutoDiag.executeDiagnostics` |
| `/system/diagnostics/{id}` | DELETE | `AutoDiag.cancelDiagnostics` |
| `/system/diagnostics/state` | GET | `AutoDiag.getDiagnosticsState` |
| `/system/diagnostics/trigger` | POST | `AutoDiag.executeTrigger` |
| `/system/diagnostics/whitelist/datamodel` | GET | `AutoDiag.getDatamodelWhiteList` |
| `/system/diagnostics/whitelist/function` | GET | `AutoDiag.getFunctionWhiteList` |
| `/system/diagnostics/context` | GET | `AutoDiag.getContext` |
| `/system/diagnostics/context` | DELETE | `AutoDiag.clearContext` |
| `/system/diagnostics/input` | POST | `AutoDiag.setUserInput` |
| `/system/dns` | GET | `DNS.getDNSServers` |

---

### Step 15 — `main.py` — wire everything up

```python
from fastapi import FastAPI
from routers import device, firewall, lan, wifi, phone, dyndns, nmc, dhcp, devices, system

app = FastAPI(title="Livebox API", version="1.0.0")

app.include_router(device.router,    prefix="/device",    tags=["Device"])
app.include_router(firewall.router,  prefix="/firewall",  tags=["Firewall"])
app.include_router(lan.router,       prefix="/lan",       tags=["LAN"])
app.include_router(wifi.router,      prefix="/wifi",      tags=["WiFi"])
app.include_router(phone.router,     prefix="/phone",     tags=["Phone"])
app.include_router(dyndns.router,    prefix="/dyndns",    tags=["DynDNS"])
app.include_router(nmc.router,       prefix="/nmc",       tags=["NMC"])
app.include_router(dhcp.router,      prefix="/dhcp",      tags=["DHCP"])
app.include_router(devices.router,   prefix="/devices",   tags=["Devices"])
app.include_router(system.router,    prefix="/system",    tags=["System"])
```

---

### Step 16 — Error handling

- Wrap every `call()` in a try/except; map Livebox error codes to HTTP status codes:
  - Permission denied → 403
  - Not found → 404
  - Validation error → 422
  - Any other box error → 502
- Use FastAPI `HTTPException` consistently.

---

### Step 17 — Configuration (`.env`)

```
LIVEBOX_URL=http://192.168.1.1
LIVEBOX_USER=admin
LIVEBOX_PASSWORD=your_password
```

---

### Step 18 — Tests

- One test file per router using `pytest-asyncio` and `httpx.AsyncClient`.
- Mock `LiveboxSession.call` to avoid needing a real box.
- Cover: happy path, 403 (permission denied), 404 (not found), validation errors.

---

## Implementation order

| Step | Description | Status |
|------|-------------|--------|
| 1 | uv project boilerplate | ✅ |
| 2 | Full project layout (target state) | ✅ |
| 3 | Core session layer (`core/config.py` + `core/session.py`) | ✅ |
| 4 | Common models (`models/common.py`) | ✅ |
| 5 | Module: Device Info | ✅ |
| 6 | Module: Firewall | ✅ |
| 7 | Module: LAN / HomeLan | ✅ |
| 8 | Module: WiFi | ✅ |
| 9 | Module: Phone / VoIP | ✅ |
| 10 | Module: DynDNS | ✅ |
| 11 | Module: NMC / System | ✅ |
| 12 | Module: DHCP | ✅ |
| 13 | Module: Devices | ✅ |
| 14 | Module: System diagnostics | ✅ |
| 15 | `main.py` — wire all routers | ✅ |
| 16 | Error handling | ✅ |
| 17 | Configuration (`.env`) | ✅ |
| 18 | Tests | ✅ |

---

## Notes

- Parameters in square brackets `[]` in the original docs are optional → `field: type | None = None` in Pydantic.
- All field names: convert `camelCase` → `snake_case` in Pydantic, use `model_config = ConfigDict(populate_by_name=True)` + `alias_generator=to_camel` for JSON serialization toward the box.
- The Livebox may not implement all modules on all firmware versions; endpoints should return `503` with a clear message when the box returns "Permission denied".
- Use `APIRouter` with a `responses` dict so the OpenAPI schema documents the 502/503 cases.
