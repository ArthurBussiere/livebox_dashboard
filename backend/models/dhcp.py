from pydantic import BaseModel


class StaticLeaseCreate(BaseModel):
    MACAddress: str
    IPAddress: str


class StaticLeaseUpdate(BaseModel):
    IPAddress: str | None = None
    Enable: bool | None = None


class LeaseTimeRequest(BaseModel):
    leasetime: int


class PoolCreate(BaseModel):
    name: str
    interface: str


class PoolAssignRequest(BaseModel):
    MACAddress: str
