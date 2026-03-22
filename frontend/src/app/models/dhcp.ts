export interface StaticLeaseCreate {
  MACAddress: string;
  IPAddress: string;
}

export interface StaticLeaseUpdate {
  IPAddress?: string;
  Enable?: boolean;
}

export interface LeaseTimeRequest {
  LeaseTime: number;
}

export interface PoolCreate {
  name: string;
  interface: string;
}

export interface PoolAssignRequest {
  MACAddress: string;
}
