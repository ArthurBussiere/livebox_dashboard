import { inject, Injectable, signal } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/api.service';
import {
  WifiConfig,
  WifiEnableRequest,
  WifiStatusRequest,
  WifiPairingRequest,
  GuestConfig,
} from '../models';

@Injectable({ providedIn: 'root' })
export class WifiService {
  private readonly api = inject(ApiService);

  readonly wifiEnabled = signal(false);

  toggle(): Observable<unknown> {
    const next = !this.wifiEnabled();
    this.wifiEnabled.set(next);
    return this.set({ Enable: next });
  }

  revertEnabled(): void {
    this.wifiEnabled.set(!this.wifiEnabled());
  }

  get(): Observable<unknown> {
    return this.api.get('/wifi');
  }

  set(body: WifiConfig): Observable<unknown> {
    return this.api.put('/wifi', body);
  }

  setEnable(body: WifiEnableRequest): Observable<unknown> {
    return this.api.patch('/wifi/enable', body);
  }

  toggleEnable(body?: WifiEnableRequest): Observable<unknown> {
    return this.api.post('/wifi/enable/toggle', body ?? {});
  }

  setStatus(body: WifiStatusRequest): Observable<unknown> {
    return this.api.patch('/wifi/status', body);
  }

  getStats(): Observable<unknown> {
    return this.api.get('/wifi/stats');
  }

  startAutoChannelSelection(): Observable<unknown> {
    return this.api.post('/wifi/channel/auto');
  }

  startPairing(body: WifiPairingRequest): Observable<unknown> {
    return this.api.post('/wifi/pairing/start', body);
  }

  stopPairing(): Observable<unknown> {
    return this.api.post('/wifi/pairing/stop');
  }

  generateSelfPIN(): Observable<unknown> {
    return this.api.post('/wifi/wps/pin');
  }

  getGuest(): Observable<unknown> {
    return this.api.get('/wifi/guest');
  }

  setGuest(body: GuestConfig): Observable<unknown> {
    return this.api.put('/wifi/guest', body);
  }
}
