from typing import Any

from pydantic import BaseModel


class DeviceFind(BaseModel):
    expression: dict | str
    flags: str = ""


class DeviceFindByIP(BaseModel):
    ipaddress: str
    ipstatus: str = ""
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


class DeviceAlternativeRules(BaseModel):
    rules: list[Any]
