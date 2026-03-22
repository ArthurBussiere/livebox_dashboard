import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/api.service';
import {
  StaticLeaseCreate,
  StaticLeaseUpdate,
  LeaseTimeRequest,
  PoolCreate,
  PoolAssignRequest,
} from '../models';

@Injectable({ providedIn: 'root' })
export class DhcpService {
  private readonly api = inject(ApiService);

  getLeases(rule?: string): Observable<unknown> {
    return this.api.get('/dhcp/leases', { rule });
  }

  getStaticLeases(): Observable<unknown> {
    return this.api.get('/dhcp/leases/static');
  }

  addStaticLease(body: StaticLeaseCreate): Observable<unknown> {
    return this.api.post('/dhcp/leases/static', body);
  }

  updateStaticLease(mac: string, body: StaticLeaseUpdate): Observable<unknown> {
    return this.api.put(`/dhcp/leases/static/${mac}`, body);
  }

  deleteStaticLease(mac: string): Observable<unknown> {
    return this.api.delete(`/dhcp/leases/static/${mac}`);
  }

  forceRenew(mac: string): Observable<unknown> {
    return this.api.post(`/dhcp/leases/static/${mac}/renew`);
  }

  addLeaseFromPool(body: PoolAssignRequest): Observable<unknown> {
    return this.api.post('/dhcp/leases/pool-assign', body);
  }

  setLeaseTime(body: LeaseTimeRequest): Observable<unknown> {
    return this.api.put('/dhcp/lease-time', body);
  }

  getPool(id: string): Observable<unknown> {
    return this.api.get(`/dhcp/pool/${id}`);
  }

  createPool(body: PoolCreate): Observable<unknown> {
    return this.api.post('/dhcp/pool', body);
  }

  clearStatistics(): Observable<unknown> {
    return this.api.delete('/dhcp/stats');
  }

  getDoraCyclesDetails(): Observable<unknown> {
    return this.api.get('/dhcp/stats/dora');
  }
}
