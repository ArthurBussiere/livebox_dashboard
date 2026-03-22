import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/api.service';
import {
  RebootRequest,
  WanModeRequest,
  LanIPConfig,
  RemoteAccessCreate,
  RemoteAccessDisable,
  IPv6Config,
  IPTVMultiscreenRequest,
  LedConfig,
  ContainerNetworkConfig,
  NetworkBRRequest,
  BackupRequest,
  WlanTimerRequest,
} from '../models';

@Injectable({ providedIn: 'root' })
export class NmcService {
  private readonly api = inject(ApiService);

  // Core config
  get(): Observable<unknown> {
    return this.api.get('/nmc');
  }

  set(body: Record<string, unknown>): Observable<unknown> {
    return this.api.put('/nmc', body);
  }

  // System control
  reboot(body: RebootRequest = { reason: 'User request' }): Observable<unknown> {
    return this.api.post('/nmc/reboot', body);
  }

  reset(body: RebootRequest = { reason: 'User request' }): Observable<unknown> {
    return this.api.post('/nmc/reset', body);
  }

  shutdown(body: RebootRequest = { reason: 'User request' }): Observable<unknown> {
    return this.api.post('/nmc/shutdown', body);
  }

  // WAN
  getWANStatus(): Observable<unknown> {
    return this.api.get('/nmc/wan/status');
  }

  getWanModeList(): Observable<unknown> {
    return this.api.get('/nmc/wan/modes');
  }

  setWanMode(body: WanModeRequest): Observable<unknown> {
    return this.api.put('/nmc/wan/mode', body);
  }

  // LAN IP
  getLANIP(): Observable<unknown> {
    return this.api.get('/nmc/lan-ip');
  }

  setLANIP(body: LanIPConfig): Observable<unknown> {
    return this.api.put('/nmc/lan-ip', body);
  }

  // Remote access
  getRemoteAccess(username?: string, usertype?: string): Observable<unknown> {
    return this.api.get('/nmc/remote-access', { username, usertype });
  }

  enableRemoteAccess(body: RemoteAccessCreate): Observable<unknown> {
    return this.api.post('/nmc/remote-access', body);
  }

  disableRemoteAccess(body: RemoteAccessDisable): Observable<unknown> {
    return this.api.deleteWithBody('/nmc/remote-access', body);
  }

  // Firmware
  updateVersionInfo(): Observable<unknown> {
    return this.api.post('/nmc/firmware/version');
  }

  checkForUpgrades(): Observable<unknown> {
    return this.api.get('/nmc/firmware/check');
  }

  // IPv6
  getIPv6(): Observable<unknown> {
    return this.api.get('/nmc/ipv6');
  }

  setIPv6(body: IPv6Config): Observable<unknown> {
    return this.api.put('/nmc/ipv6', body);
  }

  // IPTV
  getIPTVConfig(): Observable<unknown> {
    return this.api.get('/nmc/iptv/config');
  }

  getIPTVStatus(): Observable<unknown> {
    return this.api.get('/nmc/iptv/status');
  }

  getIPTVMultiScreens(): Observable<unknown> {
    return this.api.get('/nmc/iptv/multiscreen');
  }

  setIPTVMultiScreens(body: IPTVMultiscreenRequest): Observable<unknown> {
    return this.api.put('/nmc/iptv/multiscreen', body);
  }

  // LED
  getLedStatus(name: string): Observable<unknown> {
    return this.api.get(`/nmc/led/${name}`);
  }

  setLed(name: string, body: LedConfig): Observable<unknown> {
    return this.api.put(`/nmc/led/${name}`, body);
  }

  // Container network
  getContainerNetwork(): Observable<unknown> {
    return this.api.get('/nmc/container');
  }

  setContainerNetwork(body: ContainerNetworkConfig): Observable<unknown> {
    return this.api.put('/nmc/container', body);
  }

  // Network backup / restore
  getNetworkConfig(): Observable<unknown> {
    return this.api.get('/nmc/network-config');
  }

  launchNetworkBackup(body?: BackupRequest): Observable<unknown> {
    return this.api.post('/nmc/network-config/backup', body ?? {});
  }

  launchNetworkRestore(): Observable<unknown> {
    return this.api.post('/nmc/network-config/restore');
  }

  enableNetworkBR(body: NetworkBRRequest): Observable<unknown> {
    return this.api.patch('/nmc/network-config/bridge', body);
  }

  // WiFi timer
  getActivationTimer(iface: string): Observable<unknown> {
    return this.api.get(`/nmc/wlan-timer/${iface}`);
  }

  setActivationTimer(iface: string, body: WlanTimerRequest): Observable<unknown> {
    return this.api.put(`/nmc/wlan-timer/${iface}`, body);
  }

  disableActivationTimer(iface: string): Observable<unknown> {
    return this.api.delete(`/nmc/wlan-timer/${iface}`);
  }
}
