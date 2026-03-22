from pydantic import BaseModel


class DiagnosticsExecuteRequest(BaseModel):
    usr: bool | None = None


class DiagnosticsTriggerRequest(BaseModel):
    event: str


class UserInputRequest(BaseModel):
    input: str


class DNSRequest(BaseModel):
    flag: str = ""
