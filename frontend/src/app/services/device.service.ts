import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/api.service';
import { ExportRequest, RestoreRequest, RestoreExtendedRequest } from '../models';

@Injectable({ providedIn: 'root' })
export class DeviceService {
  private readonly api = inject(ApiService);

  getInfo(): Observable<unknown> {
    return this.api.get('/device/info');
  }

  getPairingInfo(): Observable<unknown> {
    return this.api.get('/device/pairing');
  }

  update(body: Record<string, unknown>): Observable<unknown> {
    return this.api.put('/device', body);
  }

  exportConfig(body: ExportRequest): Observable<unknown> {
    return this.api.post('/device/export', body);
  }

  restoreConfig(body: RestoreRequest): Observable<unknown> {
    return this.api.post('/device/config/restore', body);
  }

  restoreConfigExtended(body: RestoreExtendedRequest): Observable<unknown> {
    return this.api.post('/device/config/restore-extended', body);
  }
}
