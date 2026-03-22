export interface ExportRequest {
  fileName: string;
}

export interface RestoreRequest {
  url: string;
  username: string;
  password: string;
  fileSize?: number;
  targetFileName?: string;
  checksumAlgorithm?: string;
  checksum?: string;
}

export interface RestoreExtendedRequest extends RestoreRequest {
  caCert?: string;
  clientCert?: string;
  privateKey?: string;
}
