from pydantic import BaseModel


class RebootRequest(BaseModel):
    reason: str = "User request"


class WanModeRequest(BaseModel):
    WanMode: str
    Username: str | None = None
    Password: str | None = None


class LanIPConfig(BaseModel):
    Address: str
    Netmask: str
    DHCPEnable: bool
    DHCPMinAddress: str
    DHCPMaxAddress: str
    LeaseTime: int | None = None


class RemoteAccessCreate(BaseModel):
    username: str | None = None
    password: str | None = None
    port: int | None = None
    timeout: int | None = None
    sourcePrefix: str | None = None
    accessType: str | None = None
    secure: bool | None = None


class RemoteAccessDisable(BaseModel):
    accessType: str | None = None


class IPv6Config(BaseModel):
    Enable: bool
    UserRequested: bool | None = None
    IPv4UserRequested: bool | None = None


class IPTVMultiscreenRequest(BaseModel):
    Enable: bool


class LedConfig(BaseModel):
    state: str
    color: str


class ContainerNetworkConfig(BaseModel):
    Address: str | None = None
    Netmask: str | None = None
    DHCPEnable: bool | None = None
    DHCPMinAddress: str | None = None
    DHCPMaxAddress: str | None = None
    LeaseTime: int | None = None


class NetworkBRRequest(BaseModel):
    state: bool | None = None


class BackupRequest(BaseModel):
    delay: bool | None = None


class WlanTimerRequest(BaseModel):
    Timeout: int
