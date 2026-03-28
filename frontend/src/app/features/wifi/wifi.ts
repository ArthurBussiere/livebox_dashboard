import { Component, inject, signal, OnInit } from '@angular/core';
import { forkJoin } from 'rxjs';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { WifiService } from '../../services/wifi.service';
import { ErrorResponse } from '../../models';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { ErrorBanner } from '../../shared/error-banner/error-banner';
import { StatusBadge } from '../../shared/status-badge/status-badge';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>;

@Component({
  selector: 'app-wifi',
  templateUrl: './wifi.html',
  styleUrl: './wifi.css',
  imports: [LoadingSpinner, ErrorBanner, StatusBadge, TranslatePipe],
})
export default class Wifi implements OnInit {
  private readonly wifiService = inject(WifiService);

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly wifiEnabled = this.wifiService.wifiEnabled;
  readonly wifiData = signal<AnyRecord | null>(null);
  readonly guestData = signal<AnyRecord | null>(null);
  readonly pairing = signal(false);
ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    forkJoin({ wifi: this.wifiService.get(), guest: this.wifiService.getGuest() }).subscribe({
      next: ({ wifi, guest }) => {
        const w = this.extract(wifi);
        const g = this.extract(guest);
        this.wifiData.set(w);
        this.wifiService.wifiEnabled.set(!!w?.['Enable']);
        this.guestData.set(g);
        this.loading.set(false);
      },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.loading.set(false); },
    });
  }

  toggleWifi(checked: boolean): void {
    this.wifiService.toggle().subscribe({
      next: () => this.wifiData.update((d) => d ? { ...d, Enable: checked } : d),
      error: (err: ErrorResponse) => { this.wifiService.revertEnabled(); this.error.set(err.detail); },
    });
  }

  toggleGuest(checked: boolean): void {
    this.wifiService.setGuest({ Enable: checked }).subscribe({
      next: () => this.guestData.update((d) => d ? { ...d, Enable: checked } : d),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

startPairing(): void {
    this.wifiService.startPairing({ clientPIN: '' }).subscribe({
      next: () => this.pairing.set(true),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  stopPairing(): void {
    this.wifiService.stopPairing().subscribe({
      next: () => this.pairing.set(false),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

private static readonly GUEST_EXCLUDED = new Set(['Status', 'ActivationTimeout', 'StartTime', 'ValidTime', 'Enable', 'WifiGuestKeyConfig']);

  guestEntries(): [string, unknown][] {
    const obj = this.guestData();
    if (!obj) return [];
    return Object.entries(obj).filter(([k, v]) => !Wifi.GUEST_EXCLUDED.has(k) && typeof v !== 'object');
  }

  entries(obj: AnyRecord | null): [string, unknown][] {
    if (!obj) return [];
    return Object.entries(obj).filter(([, v]) => typeof v !== 'object');
  }

  private extract(raw: unknown): AnyRecord {
    const r = raw as AnyRecord;
    return (r?.['data'] ?? r?.['status'] ?? r) as AnyRecord;
  }
}
