import { Component, inject, signal, computed, OnInit } from '@angular/core';
import { ReactiveFormsModule, FormsModule, FormBuilder, Validators } from '@angular/forms';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { TranslationService } from '../../core/i18n/translation.service';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { DhcpService } from '../../services/dhcp.service';
import { DeviceRegistryService } from '../../core/device-registry.service';
import { ErrorResponse } from '../../models';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { ErrorBanner } from '../../shared/error-banner/error-banner';
import { StatusBadge } from '../../shared/status-badge/status-badge';
import { ConfirmDialog } from '../../shared/confirm-dialog/confirm-dialog';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>;

type DhcpTab = 'leases' | 'static' | 'settings';

@Component({
  selector: 'app-dhcp',
  templateUrl: './dhcp.html',
  styleUrl: './dhcp.css',
  imports: [ReactiveFormsModule, FormsModule, LoadingSpinner, ErrorBanner, StatusBadge, ConfirmDialog, TranslatePipe],
})
export default class Dhcp implements OnInit {
  private readonly dhcp = inject(DhcpService);
  private readonly fb = inject(FormBuilder);
  readonly registry = inject(DeviceRegistryService);
  readonly i18n = inject(TranslationService);

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly saving = signal(false);
  readonly tab = signal<DhcpTab>('static');

  readonly leases = signal<AnyRecord[]>([]);
  readonly staticLeases = signal<AnyRecord[]>([]);
  readonly doraStats = signal<AnyRecord | null>(null);
  readonly showAddStatic = signal(false);
  readonly deleteTarget = signal<AnyRecord | null>(null);

  /** Devices that don't already have a static lease (for the selector). */
  readonly availableDevices = computed(() => {
    const staticMacs = new Set(this.staticLeases().map((l) => String(l['MACAddress'] ?? '').toLowerCase()));
    return this.registry.allDevices().filter((d) => !staticMacs.has(String(d['PhysAddress'] ?? '').toLowerCase()));
  });

  readonly addStaticForm = this.fb.group({
    macAddress: ['', Validators.required],
    ipAddress: ['', Validators.required],
  });

  readonly leaseTimeForm = this.fb.group({
    leaseTime: [86400, Validators.required],
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    forkJoin({
      leases: this.dhcp.getLeases().pipe(catchError(() => of(null))),
      staticLeases: this.dhcp.getStaticLeases().pipe(catchError(() => of(null))),
      dora: this.dhcp.getDoraCyclesDetails().pipe(catchError(() => of(null))),
    }).subscribe({
      next: ({ leases, staticLeases, dora }) => {
        this.leases.set(this.extractList(leases));
        this.staticLeases.set(this.extractList(staticLeases));
        this.doraStats.set(this.extract(dora));
        this.loading.set(false);
      },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.loading.set(false); },
    });
  }

  addStaticLease(): void {
    if (this.addStaticForm.invalid) return;
    this.saving.set(true);
    const v = this.addStaticForm.value;
    this.dhcp.addStaticLease({ MACAddress: v.macAddress!, IPAddress: v.ipAddress! }).subscribe({
      next: () => {
        this.saving.set(false);
        this.showAddStatic.set(false);
        this.addStaticForm.reset();
        this.reloadStatic();
      },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.saving.set(false); },
    });
  }

  toggleLease(lease: AnyRecord): void {
    this.dhcp.updateStaticLease(lease['MACAddress'], { Enable: !lease['Enable'] }).subscribe({
      next: () => this.staticLeases.update((list) =>
        list.map((l) => l['MACAddress'] === lease['MACAddress']
          ? { ...l, Enable: !lease['Enable'] } : l)),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  forceRenew(mac: string): void {
    this.dhcp.forceRenew(mac).subscribe({
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  confirmDelete(lease: AnyRecord): void { this.deleteTarget.set(lease); }

  selectDevice(mac: string): void {
    if (!mac) return;
    const device = this.registry.byMACAddress(mac);
    if (!device) return;
    this.addStaticForm.patchValue({
      macAddress: String(device['PhysAddress'] ?? ''),
      ipAddress: String(device['IPAddress'] ?? ''),
    });
  }

  deleteStatic(): void {
    const target = this.deleteTarget();
    if (!target) return;
    this.deleteTarget.set(null);
    this.dhcp.deleteStaticLease(target['MACAddress']).subscribe({
      next: () => this.staticLeases.update((l) => l.filter((x) => x['MACAddress'] !== target['MACAddress'])),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  saveLeaseTime(): void {
    if (this.leaseTimeForm.invalid) return;
    this.saving.set(true);
    this.dhcp.setLeaseTime({ LeaseTime: this.leaseTimeForm.value.leaseTime! }).subscribe({
      next: () => this.saving.set(false),
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.saving.set(false); },
    });
  }

  entries(obj: AnyRecord | null): [string, unknown][] {
    if (!obj) return [];
    return Object.entries(obj).filter(([, v]) => typeof v !== 'object');
  }

  private reloadStatic(): void {
    this.dhcp.getStaticLeases().subscribe({
      next: (d) => this.staticLeases.set(this.extractList(d)),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  private extractList(data: unknown): AnyRecord[] {
    const r = data as AnyRecord;
    const inner = r?.['data'] ?? r?.['status'] ?? r;
    if (Array.isArray(inner)) return inner;
    if (typeof inner === 'object' && inner !== null) {
      const values = Object.values(inner as AnyRecord);
      if (values.length === 0) return [];
      if (Array.isArray(values[0])) return values[0] as AnyRecord[];
      if (typeof values[0] === 'object' && values[0] !== null) {
        // Check if values[0] is a pool/group wrapper (its own values are objects)
        // vs. a direct record (its own values are primitives)
        const nested = Object.values(values[0] as AnyRecord);
        if (nested.length > 0 && typeof nested[0] === 'object' && nested[0] !== null) {
          return nested as AnyRecord[];
        }
        return values as AnyRecord[];
      }
    }
    return [];
  }

  private extract(raw: unknown): AnyRecord {
    const r = raw as AnyRecord;
    return (r?.['data'] ?? r?.['status'] ?? r) as AnyRecord;
  }
}
