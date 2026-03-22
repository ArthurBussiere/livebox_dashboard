# Pydantic → TypeScript Model Conversion Guide

This document defines the rules and patterns for converting Pydantic models from the `livebox_api` FastAPI backend into TypeScript interfaces for this Angular project.

---

## Conversion Rules

### 1. Base Class → No Base Interface

`CamelModel` is a Python-only concern (it handles snake_case → camelCase serialization toward the Livebox box). TypeScript interfaces do **not** extend any base.

```python
# Python
class StaticLeaseCreate(CamelModel):
    mac_address: str
```
```typescript
// TypeScript
export interface StaticLeaseCreate {
  macAddress: string;
}
```

> **Rule:** All field names are written in `camelCase` in TypeScript — matching what the API actually sends/receives over the wire (the alias_generator on the Python side does the conversion automatically).

---

### 2. Type Mapping

| Python type | TypeScript type |
|---|---|
| `str` | `string` |
| `int` | `number` |
| `float` | `number` |
| `bool` | `boolean` |
| `Any` | `unknown` |
| `list[str]` | `string[]` |
| `list[int]` | `number[]` |
| `list[Any]` | `unknown[]` |
| `dict` | `Record<string, unknown>` |
| `dict \| str` | `Record<string, unknown> \| string` |

---

### 3. Optional Fields (`Type | None = None`)

Python `Type | None = None` → TypeScript optional property `?: Type`.

```python
# Python
external_port: int | None = None
description: str | None = None
```
```typescript
// TypeScript
externalPort?: number;
description?: string;
```

---

### 4. Required Fields with Defaults

If a field has a default value but is **not** `None`, keep it **required** in the TypeScript interface (the caller must still provide it explicitly, or the Angular form/service should always set it). Annotate the default inline as a comment.

```python
# Python
enable: bool = True
persistent: bool = True
reason: str = "User request"
flags: str = ""
```
```typescript
// TypeScript
enable: boolean;    // default: true
persistent: boolean; // default: true
reason: string;     // default: "User request"
flags: string;      // default: ""
```

If you need a factory helper, provide a `create*` function (see §8).

---

### 5. Model Inheritance

Python class inheritance → TypeScript `extends`.

```python
# Python
class RestoreRequest(CamelModel):
    url: str
    username: str
    password: str
    filSize: int | None = None

class RestoreExtendedRequest(RestoreRequest):
    caCert: str | None = None
    clientCert: str | None = None
    privateKey: str | None = None
```
```typescript
// TypeScript
export interface RestoreRequest {
  url: string;
  username: string;
  password: string;
  fileSize?: number;
}

export interface RestoreExtendedRequest extends RestoreRequest {
  caCert?: string;
  clientCert?: string;
  privateKey?: string;
}
```

---

### 6. Envelope / Response Models

`LiveboxResponse` and `ErrorResponse` from `common.py` map to generic response wrappers:

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

---

### 7. String Literal Unions (Documented Constraints)

Some string fields have a constrained set of values documented in comments or usage (e.g. `protocol`, `level`, `access_type`). Convert these to TypeScript union types:

```python
# Python – protocol: str  (values: "TCP" | "UDP" | "TCP,UDP")
# Python – level: str     (values: "Low" | "Medium" | "High" | "Custom")
```
```typescript
// TypeScript
export type Protocol = 'TCP' | 'UDP' | 'TCP,UDP';
export type FirewallLevel = 'Low' | 'Medium' | 'High' | 'Custom';
```

Then reference those types in the interface:
```typescript
export interface PortForwardingCreate {
  protocol: Protocol;
  // ...
}

export interface FirewallLevelRequest {
  level: FirewallLevel;
}
```

---

### 8. Factory Helper Functions (Optional)

For models that have many defaults or are frequently instantiated in forms/tests, add a `create<ModelName>` factory:

```typescript
export function createPortForwardingCreate(
  override: Partial<PortForwardingCreate> & Pick<PortForwardingCreate, 'origin' | 'sourceInterface' | 'internalPort' | 'destinationIpAddress' | 'protocol'>
): PortForwardingCreate {
  return {
    enable: true,
    persistent: true,
    ...override,
  };
}
```

---

## File Organization

Place all TypeScript model files under `src/app/models/`:

```
src/app/models/
  common.ts        ← LiveboxResponse, ErrorResponse
  lan.ts
  dhcp.ts
  device.ts
  devices.ts
  dyndns.ts
  firewall.ts
  wifi.ts
  system.ts
  nmc.ts
  index.ts         ← re-exports everything
```

Each file mirrors the Python `models/` directory. The `index.ts` barrel re-exports all interfaces and types for clean imports:

```typescript
// src/app/models/index.ts
export * from './common';
export * from './lan';
export * from './dhcp';
// ...
```

---

## Full Conversion Examples

### `dhcp.ts`

```typescript
export interface StaticLeaseCreate {
  macAddress: string;
  ipAddress: string;
}

export interface StaticLeaseUpdate {
  ipAddress?: string;
  enable?: boolean;
}

export interface LeaseTimeRequest {
  leaseTime: number;
}

export interface PoolCreate {
  name: string;
  interface: string;
}

export interface PoolAssignRequest {
  macAddress: string;
}
```

### `firewall.ts`

```typescript
export type FirewallLevel = 'Low' | 'Medium' | 'High' | 'Custom';
export type Protocol = 'TCP' | 'UDP' | 'TCP,UDP';

export interface FirewallLevelRequest {
  level: FirewallLevel;
}

export interface PingRequest {
  serviceEnable: boolean;
}

export interface PortForwardingCreate {
  origin: string;
  sourceInterface: string;
  internalPort: number;
  destinationIpAddress: string;
  protocol: Protocol;
  externalPort?: number;
  sourcePrefix?: string;
  enable: boolean;       // default: true
  persistent: boolean;   // default: true
  description?: string;
  destinationMacAddress?: string;
  leaseDuration?: number;
  upnpv1Compat?: boolean;
}

export interface PortForwardingUpdate {
  origin: string;
  sourceInterface?: string;
  internalPort?: number;
  destinationIpAddress?: string;
  protocol?: Protocol;
  externalPort?: number;
  enable?: boolean;
  persistent?: boolean;
  description?: string;
}

export interface DMZCreate {
  sourceInterface: string;
  destinationIpAddress: string;
  enable: boolean;
  sourcePrefix?: string;
}
```

### `nmc.ts`

```typescript
export interface RebootRequest {
  reason: string; // default: "User request"
}

export interface WanModeRequest {
  wanMode: string;
  username: string;
  password: string;
}

export interface LanIPConfig {
  address: string;
  netmask: string;
  dhcpEnable: boolean;
  dhcpMinAddress: string;
  dhcpMaxAddress: string;
  leaseTime: number;
}

export interface RemoteAccessCreate {
  username: string;
  password: string;
  port: number;
  timeout: number;
  sourcePrefix: string;
  accessType: string;
  secure: boolean;
}

export interface IPv6Config {
  enable: boolean;
  userRequested?: boolean;
  ipv4UserRequested?: boolean;
}

export interface LedConfig {
  state: string;
  color: string;
}
```
