import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/api.service';
import { LanStatsRequest, DeviceStatsRequest, MonitoringTestRequest } from '../models';

@Injectable({ providedIn: 'root' })
export class LanService {
  private readonly api = inject(ApiService);

  getStatus(): Observable<unknown> {
    return this.api.get('/lan/status');
  }

  getInterfacesNames(): Observable<unknown> {
    return this.api.get('/lan/interfaces');
  }

  getDevicesNames(): Observable<unknown> {
    return this.api.get('/lan/devices');
  }

  getDevicesStatus(): Observable<unknown> {
    return this.api.get('/lan/devices/status');
  }

  getWANCounters(): Observable<unknown> {
    return this.api.get('/lan/wan-counters');
  }

  getSaturationResults(): Observable<unknown> {
    return this.api.get('/lan/saturation');
  }

  getSaturationMeasures(): Observable<unknown> {
    return this.api.get('/lan/saturation/measures');
  }

  getStats(req: LanStatsRequest): Observable<unknown> {
    return this.api.get('/lan/stats', {
      seconds: req.seconds,
      numberOfReadings: req.numberOfReadings,
      interfaceNames: req.interfaceNames,
      beginTimestamp: req.beginTimestamp,
      endTimestamp: req.endTimestamp,
    });
  }

  getDeviceStats(req: DeviceStatsRequest): Observable<unknown> {
    return this.api.get('/lan/stats/device', {
      seconds: req.seconds,
      numberOfReadings: req.numberOfReadings,
      deviceName: req.deviceName,
      beginTimestamp: req.beginTimestamp,
      endTimestamp: req.endTimestamp,
    });
  }

  addDevice(mac: string): Observable<unknown> {
    return this.api.post(`/lan/devices/${mac}`);
  }

  deleteDevice(mac: string): Observable<unknown> {
    return this.api.delete(`/lan/devices/${mac}`);
  }

  startInterfaceMonitoring(body: MonitoringTestRequest): Observable<unknown> {
    return this.api.post('/lan/monitoring/interface/start', body);
  }

  stopInterfaceMonitoring(): Observable<unknown> {
    return this.api.post('/lan/monitoring/interface/stop');
  }

  startDeviceMonitoring(body: MonitoringTestRequest): Observable<unknown> {
    return this.api.post('/lan/monitoring/device/start', body);
  }

  stopDeviceMonitoring(): Observable<unknown> {
    return this.api.post('/lan/monitoring/device/stop');
  }

  exportConfig(): Observable<unknown> {
    return this.api.get('/lan/config/export');
  }

  importConfig(): Observable<unknown> {
    return this.api.post('/lan/config/import');
  }
}
