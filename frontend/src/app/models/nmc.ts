export interface RebootRequest {
  reason: string; // default: "User request"
}

export interface WanModeRequest {
  WanMode: string;
  Username?: string;
  Password?: string;
}

export interface LanIPConfig {
  Address: string;
  Netmask: string;
  DHCPEnable: boolean;
  DHCPMinAddress: string;
  DHCPMaxAddress: string;
  LeaseTime?: number;
}

export interface RemoteAccessCreate {
  username?: string;
  password?: string;
  port?: number;
  timeout?: number;
  sourcePrefix?: string;
  accessType?: string;
  secure?: boolean;
}

export interface RemoteAccessDisable {
  accessType?: string;
}

export interface IPv6Config {
  Enable: boolean;
  UserRequested?: boolean;
  IPv4UserRequested?: boolean;
}

export interface IPTVMultiscreenRequest {
  Enable: boolean;
}

export interface LedConfig {
  state: string;
  color: string;
}

export interface ContainerNetworkConfig {
  Address?: string;
  Netmask?: string;
  DHCPEnable?: boolean;
  DHCPMinAddress?: string;
  DHCPMaxAddress?: string;
  LeaseTime?: number;
}

export interface NetworkBRRequest {
  state?: boolean;
}

export interface BackupRequest {
  delay?: boolean;
}

export interface WlanTimerRequest {
  Timeout: number;
}
