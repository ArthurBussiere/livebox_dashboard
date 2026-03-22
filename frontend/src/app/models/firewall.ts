export type FirewallLevel = 'Low' | 'Medium' | 'High' | 'Custom';
export type Protocol = 'TCP' | 'UDP' | 'TCP,UDP';

export interface FirewallLevelRequest {
  level: FirewallLevel;
}

export interface PingRequest {
  service_enable: boolean;
}

export interface PortForwardingCreate {
  origin: string;
  sourceInterface: string;
  internalPort: string;
  destinationIPAddress: string;
  protocol: Protocol;
  externalPort?: string;
  sourcePrefix?: string;
  enable: boolean;              // default: true
  persistent: boolean;          // default: true
  description?: string;
  destinationMACAddress?: string;
  leaseDuration?: number;
  upnpv1Compat?: boolean;
}

export interface PortForwardingUpdate {
  origin: string;
  sourceInterface?: string;
  internalPort?: string;
  destinationIPAddress?: string;
  protocol?: Protocol;
  externalPort?: string;
  enable?: boolean;
  persistent?: boolean;
  description?: string;
}

export interface PortForwardingEnableRequest {
  origin: string;
  enable: boolean;
}

export interface PortForwardingRefreshRequest {
  origin: string;
  description?: string;
  persistent?: boolean;
  leaseDuration?: number;
}

export interface ProtocolForwardingCreate {
  destinationIPAddress: string;
  protocol: string;
  sourceInterface?: string;
  sourcePrefix?: string;
  enable: boolean;     // default: true
  persistent: boolean; // default: true
  description?: string;
}

export interface PinholeCreate {
  origin: string;
  sourceInterface: string;
  destinationPort: string;
  destinationIPAddress: string;
  protocol: string;
  sourcePort?: string;
  sourcePrefix?: string;
  ipversion?: number;
  enable: boolean;     // default: true
  persistent: boolean; // default: true
  description?: string;
  destinationMACAddress?: string;
}

export interface DMZCreate {
  sourceInterface: string;
  destinationIPAddress: string;
  enable: boolean;
  sourcePrefix?: string;
}

export interface RedirectCreate {
  protocol: string;
  sourceInterface?: string;
  destinationPort?: string;
  ipversion?: number;
  enable: boolean; // default: true
}

export interface CustomRuleCreate {
  action: string;
  chain?: string;
  destinationPort?: string;
  sourcePort?: string;
  destinationPrefix?: string;
  sourcePrefix?: string;
  protocol?: string;
  ipversion?: number;
  enable: boolean;     // default: true
  description?: string;
  destinationMAC?: string;
  sourceMAC?: string;
  persistent: boolean; // default: true
}

export interface ListEntryCreate {
  destinationPrefix: string;
  protocol: string;
  enable: boolean; // default: true
  sourcePrefix?: string;
}
