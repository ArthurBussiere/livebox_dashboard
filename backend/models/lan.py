from pydantic import BaseModel


class LanStatsRequest(BaseModel):
    Seconds: int
    NumberOfReadings: int
    InterfaceName: list[str]
    BeginTrafficTimestamp: int | None = None
    EndTrafficTimestamp: int | None = None


class DeviceStatsRequest(BaseModel):
    Seconds: int
    NumberOfReadings: int
    DeviceName: str
    BeginTrafficTimestamp: int | None = None
    EndTrafficTimestamp: int | None = None


class MonitoringTestRequest(BaseModel):
    duration: int
    interval: int
