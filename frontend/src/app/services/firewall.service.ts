import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/api.service';
import {
  FirewallLevelRequest,
  PingRequest,
  PortForwardingCreate,
  PortForwardingUpdate,
  PortForwardingEnableRequest,
  PortForwardingRefreshRequest,
  ProtocolForwardingCreate,
  PinholeCreate,
  DMZCreate,
  RedirectCreate,
  CustomRuleCreate,
  ListEntryCreate,
} from '../models';

@Injectable({ providedIn: 'root' })
export class FirewallService {
  private readonly api = inject(ApiService);

  // Level
  getLevel(): Observable<unknown> {
    return this.api.get('/firewall/level');
  }

  setLevel(body: FirewallLevelRequest): Observable<unknown> {
    return this.api.put('/firewall/level', body);
  }

  getIPv6Level(): Observable<unknown> {
    return this.api.get('/firewall/ipv6-level');
  }

  setIPv6Level(body: FirewallLevelRequest): Observable<unknown> {
    return this.api.put('/firewall/ipv6-level', body);
  }

  commit(): Observable<unknown> {
    return this.api.post('/firewall/commit');
  }

  // Ping
  getRespondToPing(iface: string): Observable<unknown> {
    return this.api.get(`/firewall/ping/${iface}`);
  }

  setRespondToPing(iface: string, body: PingRequest): Observable<unknown> {
    return this.api.put(`/firewall/ping/${iface}`, body);
  }

  // Port forwarding
  getPortForwarding(id?: string): Observable<unknown> {
    return this.api.get('/firewall/port-forwarding', { id });
  }

  createPortForwarding(body: PortForwardingCreate): Observable<unknown> {
    return this.api.post('/firewall/port-forwarding', body);
  }

  updatePortForwarding(id: string, body: PortForwardingUpdate): Observable<unknown> {
    return this.api.put(`/firewall/port-forwarding/${id}`, body);
  }

  deletePortForwarding(id: string, origin: string): Observable<unknown> {
    return this.api.delete(`/firewall/port-forwarding/${id}`, { origin });
  }

  enablePortForwarding(id: string, body: PortForwardingEnableRequest): Observable<unknown> {
    return this.api.patch(`/firewall/port-forwarding/${id}/enable`, body);
  }

  refreshPortForwarding(id: string, body: PortForwardingRefreshRequest): Observable<unknown> {
    return this.api.post(`/firewall/port-forwarding/${id}/refresh`, body);
  }

  // Protocol forwarding
  getProtocolForwarding(id?: string): Observable<unknown> {
    return this.api.get('/firewall/protocol-forwarding', { id });
  }

  createProtocolForwarding(body: ProtocolForwardingCreate): Observable<unknown> {
    return this.api.post('/firewall/protocol-forwarding', body);
  }

  deleteProtocolForwarding(id: string): Observable<unknown> {
    return this.api.delete(`/firewall/protocol-forwarding/${id}`);
  }

  // Pinhole (IPv6)
  getPinhole(id?: string, origin?: string): Observable<unknown> {
    return this.api.get('/firewall/pinhole', { id, origin });
  }

  createPinhole(body: PinholeCreate): Observable<unknown> {
    return this.api.post('/firewall/pinhole', body);
  }

  deletePinhole(id: string, origin: string): Observable<unknown> {
    return this.api.delete(`/firewall/pinhole/${id}`, { origin });
  }

  // DMZ
  getDMZ(id?: string): Observable<unknown> {
    return this.api.get('/firewall/dmz', { id });
  }

  createDMZ(body: DMZCreate): Observable<unknown> {
    return this.api.post('/firewall/dmz', body);
  }

  deleteDMZ(id: string): Observable<unknown> {
    return this.api.delete(`/firewall/dmz/${id}`);
  }

  // Redirect
  getRedirect(id?: string): Observable<unknown> {
    return this.api.get('/firewall/redirect', { id });
  }

  createRedirect(body: RedirectCreate): Observable<unknown> {
    return this.api.post('/firewall/redirect', body);
  }

  deleteRedirect(id: string): Observable<unknown> {
    return this.api.delete(`/firewall/redirect/${id}`);
  }

  // Custom rules
  getCustomRules(id?: string, chain?: string): Observable<unknown> {
    return this.api.get('/firewall/custom-rules', { id, chain });
  }

  createCustomRule(body: CustomRuleCreate): Observable<unknown> {
    return this.api.post('/firewall/custom-rules', body);
  }

  deleteCustomRule(id: string, chain?: string): Observable<unknown> {
    return this.api.delete(`/firewall/custom-rules/${id}`, { chain });
  }

  // List entries
  getListEntries(listName: string, entryId?: string): Observable<unknown> {
    return this.api.get(`/firewall/lists/${listName}`, { entryId });
  }

  setListEntry(listName: string, entryId: string, body: ListEntryCreate): Observable<unknown> {
    return this.api.post(`/firewall/lists/${listName}/${entryId}`, body);
  }

  deleteListEntry(listName: string, entryId: string): Observable<unknown> {
    return this.api.delete(`/firewall/lists/${listName}/${entryId}`);
  }
}
