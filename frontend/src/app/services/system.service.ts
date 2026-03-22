import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/api.service';
import {
  DiagnosticsExecuteRequest,
  DiagnosticsTriggerRequest,
  UserInputRequest,
  DNSRequest,
} from '../models';

@Injectable({ providedIn: 'root' })
export class SystemService {
  private readonly api = inject(ApiService);

  // Diagnostics
  listDiagnostics(): Observable<unknown> {
    return this.api.get('/system/diagnostics');
  }

  getDiagnosticsState(): Observable<unknown> {
    return this.api.get('/system/diagnostics/state');
  }

  executeTrigger(body: DiagnosticsTriggerRequest): Observable<unknown> {
    return this.api.post('/system/diagnostics/trigger', body);
  }

  getDatamodelWhiteList(): Observable<unknown> {
    return this.api.get('/system/diagnostics/whitelist/datamodel');
  }

  getFunctionWhiteList(): Observable<unknown> {
    return this.api.get('/system/diagnostics/whitelist/function');
  }

  getContext(): Observable<unknown> {
    return this.api.get('/system/diagnostics/context');
  }

  clearContext(): Observable<unknown> {
    return this.api.delete('/system/diagnostics/context');
  }

  setUserInput(body: UserInputRequest): Observable<unknown> {
    return this.api.post('/system/diagnostics/input', body);
  }

  executeDiagnostics(id: string, body?: DiagnosticsExecuteRequest): Observable<unknown> {
    return this.api.post(`/system/diagnostics/${id}`, body ?? {});
  }

  cancelDiagnostics(id?: string): Observable<unknown> {
    return id
      ? this.api.delete(`/system/diagnostics/${id}`)
      : this.api.delete('/system/diagnostics');
  }

  // DNS
  getDNSServers(req?: DNSRequest): Observable<unknown> {
    return this.api.get('/system/dns', { flag: req?.flag });
  }
}
