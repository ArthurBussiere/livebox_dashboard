from pydantic import BaseModel


class FirewallLevelRequest(BaseModel):
    level: str


class PingRequest(BaseModel):
    service_enable: bool


class PortForwardingCreate(BaseModel):
    origin: str
    sourceInterface: str
    internalPort: str
    destinationIPAddress: str
    protocol: str
    externalPort: str | None = None
    sourcePrefix: str | None = None
    enable: bool = True
    persistent: bool = True
    description: str | None = None
    destinationMACAddress: str | None = None
    leaseDuration: int | None = None
    upnpv1Compat: bool | None = None


class PortForwardingUpdate(BaseModel):
    origin: str
    sourceInterface: str | None = None
    internalPort: str | None = None
    destinationIPAddress: str | None = None
    protocol: str | None = None
    externalPort: str | None = None
    enable: bool | None = None
    persistent: bool | None = None
    description: str | None = None


class PortForwardingEnableRequest(BaseModel):
    origin: str
    enable: bool


class PortForwardingRefreshRequest(BaseModel):
    origin: str
    description: str | None = None
    persistent: bool | None = None
    leaseDuration: int | None = None


class ProtocolForwardingCreate(BaseModel):
    destinationIPAddress: str
    protocol: str
    sourceInterface: str | None = None
    sourcePrefix: str | None = None
    enable: bool = True
    persistent: bool = True
    description: str | None = None


class PinholeCreate(BaseModel):
    origin: str
    sourceInterface: str
    destinationPort: str
    destinationIPAddress: str
    protocol: str
    sourcePort: str | None = None
    sourcePrefix: str | None = None
    ipversion: int | None = None
    enable: bool = True
    persistent: bool = True
    description: str | None = None
    destinationMACAddress: str | None = None


class DMZCreate(BaseModel):
    sourceInterface: str
    destinationIPAddress: str
    enable: bool
    sourcePrefix: str | None = None


class RedirectCreate(BaseModel):
    protocol: str
    sourceInterface: str | None = None
    destinationPort: str | None = None
    ipversion: int | None = None
    enable: bool = True


class CustomRuleCreate(BaseModel):
    action: str
    chain: str | None = None
    destinationPort: str | None = None
    sourcePort: str | None = None
    destinationPrefix: str | None = None
    sourcePrefix: str | None = None
    protocol: str | None = None
    ipversion: int | None = None
    enable: bool = True
    description: str | None = None
    destinationMAC: str | None = None
    sourceMAC: str | None = None
    persistent: bool = True


class ListEntryCreate(BaseModel):
    destinationPrefix: str
    protocol: str
    enable: bool = True
    sourcePrefix: str | None = None
