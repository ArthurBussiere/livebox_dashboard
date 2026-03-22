export interface WifiConfig {
  Enable?: boolean;
  Status?: boolean;
  ConfigurationMode?: boolean;
  TriggerAutoChannelSelection?: boolean;
}

export interface WifiEnableRequest {
  value: boolean;
  temporary?: boolean;
  source?: string;
}

export interface WifiStatusRequest {
  status: boolean;
}

export interface WifiPairingRequest {
  clientPin: string;
}

export interface GuestConfig {
  enable: boolean;
}
