from pydantic import BaseModel


class ExportRequest(BaseModel):
    fileName: str


class RestoreRequest(BaseModel):
    URL: str
    Username: str
    Password: str
    FileSize: int | None = None
    TargetFileName: str | None = None
    CheckSumAlgorithm: str | None = None
    CheckSum: str | None = None


class RestoreExtendedRequest(RestoreRequest):
    CACert: str | None = None
    ClientCert: str | None = None
    PrivateKey: str | None = None
