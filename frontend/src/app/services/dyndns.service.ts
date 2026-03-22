import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/api.service';
import { DynDNSHostCreate, DynDNSEnableRequest } from '../models';

@Injectable({ providedIn: 'root' })
export class DyndnsService {
  private readonly api = inject(ApiService);

  getHosts(): Observable<unknown> {
    return this.api.get('/dyndns');
  }

  addHost(body: DynDNSHostCreate): Observable<unknown> {
    return this.api.post('/dyndns', body);
  }

  deleteHost(hostname: string): Observable<unknown> {
    return this.api.delete(`/dyndns/${hostname}`);
  }

  getServices(): Observable<unknown> {
    return this.api.get('/dyndns/services');
  }

  getGlobalEnable(): Observable<unknown> {
    return this.api.get('/dyndns/enable');
  }

  setGlobalEnable(body: DynDNSEnableRequest): Observable<unknown> {
    return this.api.patch('/dyndns/enable', body);
  }

  getEnableOnCgnat(): Observable<unknown> {
    return this.api.get('/dyndns/cgnat');
  }

  setEnableOnCgnat(body: DynDNSEnableRequest): Observable<unknown> {
    return this.api.patch('/dyndns/cgnat', body);
  }
}
