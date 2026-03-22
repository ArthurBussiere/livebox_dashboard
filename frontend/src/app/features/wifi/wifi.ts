import { Component, inject, signal, OnInit } from '@angular/core';
import { ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { WifiService } from '../../services/wifi.service';
import { ErrorResponse } from '../../models';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { ErrorBanner } from '../../shared/error-banner/error-banner';
import { StatusBadge } from '../../shared/status-badge/status-badge';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>;

type WifiTab = 'main' | 'guest' | 'wps';

@Component({
  selector: 'app-wifi',
  templateUrl: './wifi.html',
  styleUrl: './wifi.css',
  imports: [ReactiveFormsModule, LoadingSpinner, ErrorBanner, StatusBadge],
})
export default class Wifi implements OnInit {
  private readonly wifiService = inject(WifiService);
  private readonly fb = inject(FormBuilder);

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly saving = signal(false);
  readonly tab = signal<WifiTab>('main');

  readonly wifiData = signal<AnyRecord | null>(null);
  readonly guestData = signal<AnyRecord | null>(null);
  readonly stats = signal<AnyRecord | null>(null);
  readonly pairing = signal(false);
  readonly generatedPin = signal<string | null>(null);

  readonly mainForm = this.fb.group({
    enable: [false],
    configurationMode: [false],
  });

  ngOnInit(): void {
    this.load();
    this.wifiService.getStats().subscribe({ next: (d) => this.stats.set(this.extract(d)) });
  }

  load(): void {
    this.loading.set(true);
    forkJoin({ wifi: this.wifiService.get(), guest: this.wifiService.getGuest() }).subscribe({
      next: ({ wifi, guest }) => {
        const w = this.extract(wifi);
        const g = this.extract(guest);
        this.wifiData.set(w);
        this.guestData.set(g);
        this.mainForm.patchValue({
          enable: !!w?.['Enable'],
          configurationMode: !!w?.['ConfigurationMode'],
        });
        this.loading.set(false);
      },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.loading.set(false); },
    });
  }

  toggleWifi(checked: boolean): void {
    this.wifiService.setEnable({ value: checked }).subscribe({
      next: () => this.wifiData.update((d) => d ? { ...d, Enable: checked } : d),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  toggleGuest(checked: boolean): void {
    this.wifiService.setGuest({ enable: checked }).subscribe({
      next: () => this.guestData.update((d) => d ? { ...d, Enable: checked } : d),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  saveMain(): void {
    this.saving.set(true);
    const v = this.mainForm.value;
    this.wifiService.set({ Enable: !!v.enable, ConfigurationMode: v.configurationMode ?? undefined })
      .subscribe({
        next: () => this.saving.set(false),
        error: (err: ErrorResponse) => { this.error.set(err.detail); this.saving.set(false); },
      });
  }

  startPairing(): void {
    this.wifiService.startPairing({ clientPin: '' }).subscribe({
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

  generatePin(): void {
    this.wifiService.generateSelfPIN().subscribe({
      next: (d) => this.generatedPin.set(String(this.extract(d)?.['PIN'] ?? d ?? '?')),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
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
