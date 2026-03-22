export interface DeviceFind {
  expression: Record<string, unknown> | string;
  flags: string; // default: ""
}

export interface DeviceFindByIP {
  ipAddress: string;
  ipStatus: string;  // default: ""
  flags: string;     // default: ""
}

export interface DeviceSetName {
  name: string;
  source: string;
}

export interface DeviceSetType {
  type: string;
  source: string;
}

export interface DeviceTagRequest {
  expression: string; // default: ""
  traverse: string;   // default: ""
}

export interface DeviceAlternativeRequest {
  alternative: string;
}

export interface DeviceAlternativeRules {
  rules: unknown[];
}
