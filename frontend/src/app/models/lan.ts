export interface LanStatsRequest {
  seconds: number;
  numberOfReadings: number;
  interfaceNames: string[];
  beginTimestamp?: number;
  endTimestamp?: number;
}

export interface DeviceStatsRequest {
  seconds: number;
  numberOfReadings: number;
  deviceName: string;
  beginTimestamp?: number;
  endTimestamp?: number;
}

export interface MonitoringTestRequest {
  duration: number;
  interval: number;
}
