from pydantic import BaseModel


class DynDNSHostCreate(BaseModel):
    service: str
    hostname: str
    username: str
    password: str
    enable: bool = True


class DynDNSEnableRequest(BaseModel):
    enable: bool
