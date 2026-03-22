import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/api.service';
import {
  DeviceFind,
  DeviceFindByIP,
  DeviceSetName,
  DeviceSetType,
  DeviceTagRequest,
  DeviceAlternativeRequest,
  DeviceAlternativeRules,
} from '../models';

@Injectable({ providedIn: 'root' })
export class DevicesService {
  private readonly api = inject(ApiService);

  getAll(expression?: string, flags?: string): Observable<unknown> {
    return this.api.get('/devices', { expression, flags });
  }

  find(body: DeviceFind): Observable<unknown> {
    return this.api.post('/devices/find', body);
  }

  findByIP(req: DeviceFindByIP): Observable<unknown> {
    return this.api.get('/devices/by-ip', {
      ipAddress: req.ipAddress,
      ipStatus: req.ipStatus,
      flags: req.flags,
    });
  }

  fetchDevice(key: string, flags?: string): Observable<unknown> {
    return this.api.get(`/devices/${key}`, { flags });
  }

  set(key: string, body: Record<string, unknown>): Observable<unknown> {
    return this.api.put(`/devices/${key}`, body);
  }

  destroyDevice(key: string): Observable<unknown> {
    return this.api.delete(`/devices/${key}`);
  }

  setName(key: string, body: DeviceSetName): Observable<unknown> {
    return this.api.put(`/devices/${key}/name`, body);
  }

  addName(key: string, body: DeviceSetName): Observable<unknown> {
    return this.api.post(`/devices/${key}/name`, body);
  }

  removeName(key: string, source: string): Observable<unknown> {
    return this.api.delete(`/devices/${key}/name`, { source });
  }

  setType(key: string, body: DeviceSetType): Observable<unknown> {
    return this.api.put(`/devices/${key}/type`, body);
  }

  removeType(key: string, source: string): Observable<unknown> {
    return this.api.delete(`/devices/${key}/type`, { source });
  }

  hasTag(key: string, tag: string, body?: DeviceTagRequest): Observable<unknown> {
    return this.api.get(`/devices/${key}/tags/${tag}`, {
      expression: body?.expression,
      traverse: body?.traverse,
    });
  }

  setTag(key: string, tag: string, body: DeviceTagRequest): Observable<unknown> {
    return this.api.put(`/devices/${key}/tags/${tag}`, body);
  }

  clearTag(key: string, tag: string, body?: DeviceTagRequest): Observable<unknown> {
    return this.api.delete(`/devices/${key}/tags/${tag}`, {
      expression: body?.expression,
      traverse: body?.traverse,
    });
  }

  getTopology(
    key: string,
    expression?: string,
    traverse?: string,
    flags?: string,
  ): Observable<unknown> {
    return this.api.get(`/devices/${key}/topology`, { expression, traverse, flags });
  }

  getParameters(
    key: string,
    parameter?: string,
    expression?: string,
    traverse?: string,
  ): Observable<unknown> {
    return this.api.get(`/devices/${key}/parameters`, { parameter, expression, traverse });
  }

  setAlternative(key: string, body: DeviceAlternativeRequest): Observable<unknown> {
    return this.api.put(`/devices/${key}/alternative`, body);
  }

  removeAlternative(key: string, body: DeviceAlternativeRequest): Observable<unknown> {
    return this.api.deleteWithBody(`/devices/${key}/alternative`, body);
  }

  setAlternativeRules(key: string, body: DeviceAlternativeRules): Observable<unknown> {
    return this.api.put(`/devices/${key}/alternative/rules`, body);
  }
}
