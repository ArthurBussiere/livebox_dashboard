import { Component, inject, signal, OnInit } from '@angular/core';
import { ReactiveFormsModule, FormBuilder } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { NmcService } from '../../services/nmc.service';
import { DeviceService } from '../../services/device.service';
import { SystemService } from '../../services/system.service';
import { ErrorResponse } from '../../models';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { ErrorBanner } from '../../shared/error-banner/error-banner';
import { ConfirmDialog } from '../../shared/confirm-dialog/confirm-dialog';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>;

type SysTab = 'ipv6' | 'device' | 'diag' | 'control';

@Component({
  selector: 'app-system',
  templateUrl: './system.html',
  styleUrl: './system.css',
  imports: [ReactiveFormsModule, LoadingSpinner, ErrorBanner, ConfirmDialog],
})
export default class System implements OnInit {
  private readonly nmc = inject(NmcService);
  private readonly device = inject(DeviceService);
  private readonly sys = inject(SystemService);
  private readonly fb = inject(FormBuilder);

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly saving = signal(false);
  readonly tab = signal<SysTab>('ipv6');

  readonly ipv6Config = signal<AnyRecord | null>(null);
  readonly deviceInfo = signal<AnyRecord | null>(null);
  readonly diagnostics = signal<AnyRecord[]>([]);
  readonly firmwareInfo = signal<AnyRecord | null>(null);

  readonly confirmAction = signal<'reboot' | 'reset' | null>(null);

  readonly ipv6Form = this.fb.group({
    enable: [false],
    userRequested: [false],
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    forkJoin({
      ipv6: this.nmc.getIPv6(),
      devInfo: this.device.getInfo(),
      diag: this.sys.listDiagnostics(),
    }).subscribe({
      next: ({ ipv6, devInfo, diag }) => {
        const v6 = this.extract(ipv6);
        this.ipv6Config.set(v6);
        this.ipv6Form.patchValue({ enable: !!v6?.['Enable'], userRequested: !!v6?.['UserRequested'] });
        this.deviceInfo.set(this.extract(devInfo));
        this.diagnostics.set(this.extractList(diag));
        this.loading.set(false);
      },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.loading.set(false); },
    });
  }

  saveIPv6(): void {
    this.saving.set(true);
    const v = this.ipv6Form.value;
    this.nmc.setIPv6({ Enable: !!v.enable, UserRequested: !!v.userRequested }).subscribe({
      next: () => this.saving.set(false),
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.saving.set(false); },
    });
  }

  checkFirmware(): void {
    this.nmc.checkForUpgrades().subscribe({
      next: (d) => this.firmwareInfo.set(this.extract(d)),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  runDiag(id: string): void {
    this.sys.executeDiagnostics(id).subscribe({
      error: (err: ErrorResponse) => this.error.set(err.detail),
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

  entries(obj: AnyRecord | null | unknown): [string, unknown][] {
    if (!obj || typeof obj !== 'object') return [];
    return Object.entries(obj as AnyRecord).filter(([, v]) => typeof v !== 'object');
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
