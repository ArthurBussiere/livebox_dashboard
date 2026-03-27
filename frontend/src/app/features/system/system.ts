import { Component, inject, signal, OnInit } from '@angular/core';
import { ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { NmcService } from '../../services/nmc.service';
import { DeviceService } from '../../services/device.service';
import { ErrorResponse } from '../../models';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { ErrorBanner } from '../../shared/error-banner/error-banner';
import { ConfirmDialog } from '../../shared/confirm-dialog/confirm-dialog';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>;

type SysTab = 'ipv6' | 'device' | 'control';

@Component({
  selector: 'app-system',
  templateUrl: './system.html',
  styleUrl: './system.css',
  imports: [ReactiveFormsModule, LoadingSpinner, ErrorBanner, ConfirmDialog],
})
export default class System implements OnInit {
  private readonly nmc = inject(NmcService);
  private readonly device = inject(DeviceService);
private readonly fb = inject(FormBuilder);

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly saving = signal(false);
  readonly tab = signal<SysTab>('device');

  readonly ipv6Config = signal<AnyRecord | null>(null);
  readonly deviceInfo = signal<AnyRecord | null>(null);
readonly confirmAction = signal<'reboot' | 'reset' | null>(null);

  readonly ipv6Form = this.fb.group({
    enable: [false],
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    forkJoin({
      ipv6: this.nmc.getIPv6(),
      devInfo: this.device.getInfo(),
    }).subscribe({
      next: ({ ipv6, devInfo }) => {
        const v6 = this.extract(ipv6);
        this.ipv6Config.set(v6);
        this.ipv6Form.patchValue({ enable: !!v6?.['Enable'] });
        this.deviceInfo.set(this.extract(devInfo));
        this.loading.set(false);
      },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.loading.set(false); },
    });
  }

  saveIPv6(): void {
    this.saving.set(true);
    const v = this.ipv6Form.value;
    this.nmc.setIPv6({ Enable: !!v.enable }).subscribe({
      next: () => this.saving.set(false),
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.saving.set(false); },
    });
  }

reboot(): void {
    this.confirmAction.set(null);
    this.nmc.reboot().subscribe({ error: (err: ErrorResponse) => this.error.set(err.detail) });
  }

  reset(): void {
    this.confirmAction.set(null);
    this.nmc.reset().subscribe({ error: (err: ErrorResponse) => this.error.set(err.detail) });
  }

  confirmDialog(): string {
    const a = this.confirmAction();
    return a === 'reboot'
      ? 'Reboot the Livebox? All connections will be interrupted for ~60s.'
      : 'Factory reset the Livebox? All settings will be lost.';
  }

  onConfirm(): void {
    this.confirmAction() === 'reboot' ? this.reboot() : this.reset();
  }

  entries(obj: unknown, prefix = ''): [string, unknown][] {
    if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return [];
    const result: [string, unknown][] = [];
    for (const [k, v] of Object.entries(obj as AnyRecord)) {
      const key = prefix ? `${prefix}.${k}` : k;
      if (v !== null && typeof v === 'object' && !Array.isArray(v)) {
        result.push(...this.entries(v, key));
      } else if (!Array.isArray(v) && v !== null && v !== undefined) {
        result.push([key, v]);
      }
    }
    return result;
  }

  private extractList(data: unknown): AnyRecord[] {
    const r = data as AnyRecord;
    const inner = r?.['data'] ?? r?.['status'] ?? r;
    if (Array.isArray(inner)) return inner;
    if (typeof inner === 'object' && inner !== null) {
      const first = Object.values(inner as AnyRecord)[0];
      if (Array.isArray(first)) return first;
    }
    return [];
  }

  private extract(raw: unknown): AnyRecord {
    const r = raw as AnyRecord;
    return (r?.['data'] ?? r?.['status'] ?? r) as AnyRecord;
  }
}
