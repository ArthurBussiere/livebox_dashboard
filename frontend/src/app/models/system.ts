export interface DiagnosticsExecuteRequest {
  usr?: boolean;
}

export interface DiagnosticsTriggerRequest {
  event: string;
}

export interface UserInputRequest {
  input: string;
}

export interface DNSRequest {
  flag: string; // default: ""
}
