from pydantic import BaseModel


class WifiConfig(BaseModel):
    Enable: bool | None = None
    Status: bool | None = None
    ConfigurationMode: bool | None = None
    TriggerAutoChannelSelection: bool | None = None


class WifiEnableRequest(BaseModel):
    value: bool
    temporary: bool | None = None
    source: str | None = None


class WifiStatusRequest(BaseModel):
    Status: bool


class WifiPairingRequest(BaseModel):
    clientPIN: str


class GuestConfig(BaseModel):
    Enable: bool
