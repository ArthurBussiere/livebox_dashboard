import { inject, Injectable, signal } from '@angular/core';
import { DevicesService } from '../services/devices.service';
import { ErrorResponse } from '../models';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>;

@Injectable({ providedIn: 'root' })
export class DeviceRegistryService {
  private readonly devices = inject(DevicesService);

  // Three indexes built from the same device list
  private readonly _list = signal<AnyRecord[]>([]);
  private readonly _byClientId = signal<Map<string, AnyRecord>>(new Map());
  private readonly _byIp = signal<Map<string, AnyRecord>>(new Map());
  private readonly _byMac = signal<Map<string, AnyRecord>>(new Map());

  readonly loaded = signal(false);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  /** Full list of client devices (excludes Livebox interfaces and non-client entries). */
  allDevices(): AnyRecord[] {
    return this._list();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.devices.getAll().subscribe({
      next: (raw) => {
        const r = raw as AnyRecord;
        const list: AnyRecord[] = Array.isArray(r?.['status']) ? r['status'] : [];

        const byClientId = new Map<string, AnyRecord>();
        const byIp = new Map<string, AnyRecord>();
        const byMac = new Map<string, AnyRecord>();

        // Only keep real client devices: must have a ClientID and PhysAddress
        const clients: AnyRecord[] = [];

        for (const d of list) {
          const clientId = String(d['ClientID'] ?? '').toLowerCase();
          const ip = String(d['IPAddress'] ?? '');
          const mac = String(d['PhysAddress'] ?? '').toLowerCase();
          if (clientId) byClientId.set(clientId, d);
          if (ip) byIp.set(ip, d);
          if (mac) byMac.set(mac, d);
          if (clientId && mac) clients.push(d);
        }

        this._list.set(clients);
        this._byClientId.set(byClientId);
        this._byIp.set(byIp);
        this._byMac.set(byMac);
        this.loaded.set(true);
        this.loading.set(false);
      },
      error: (err: ErrorResponse) => {
        this.error.set(err.detail ?? 'Failed to load devices');
        this.loading.set(false);
      },
    });
  }

  /** Look up a device by ClientID (case-insensitive). */
  byClientID(clientId: string | undefined): AnyRecord | null {
    return this._byClientId().get((clientId ?? '').toLowerCase()) ?? null;
  }

  /** Look up a device by its primary IPv4 address. */
  byIPAddress(ip: string | undefined): AnyRecord | null {
    return this._byIp().get(ip ?? '') ?? null;
  }

  /** Look up a device by MAC address (case-insensitive). */
  byMACAddress(mac: string | undefined): AnyRecord | null {
    return this._byMac().get((mac ?? '').toLowerCase()) ?? null;
  }

  /** Convenience: return the device Name or empty string. */
  nameFor(device: AnyRecord | null): string {
    return device?.['Name'] ?? '';
  }
}
