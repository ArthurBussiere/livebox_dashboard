import { Component, inject, signal, OnInit } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { DyndnsService } from '../../services/dyndns.service';
import { DynDNSHostCreate, ErrorResponse } from '../../models';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { ErrorBanner } from '../../shared/error-banner/error-banner';
import { StatusBadge } from '../../shared/status-badge/status-badge';
import { ConfirmDialog } from '../../shared/confirm-dialog/confirm-dialog';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>;

@Component({
  selector: 'app-dyndns',
  templateUrl: './dyndns.html',
  styleUrl: './dyndns.css',
  imports: [ReactiveFormsModule, LoadingSpinner, ErrorBanner, StatusBadge, ConfirmDialog],
})
export default class Dyndns implements OnInit {
  private readonly dyndns = inject(DyndnsService);
  private readonly fb = inject(FormBuilder);

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly saving = signal(false);

  readonly globalEnabled = signal(false);
  readonly cgnatEnabled = signal(false);
  readonly hosts = signal<AnyRecord[]>([]);
  readonly services = signal<string[]>([]);

  readonly showAddForm = signal(false);
  readonly deleteTarget = signal<string | null>(null);

  readonly addForm = this.fb.group({
    service: ['', Validators.required],
    hostname: ['', Validators.required],
    username: ['', Validators.required],
    password: ['', Validators.required],
    enable: [true],
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    forkJoin({
      hosts: this.dyndns.getHosts(),
      services: this.dyndns.getServices(),
      enabled: this.dyndns.getGlobalEnable(),
      cgnat: this.dyndns.getEnableOnCgnat(),
    }).subscribe({
      next: ({ hosts, services, enabled, cgnat }) => {
        this.hosts.set(this.extractList(hosts));
        this.services.set(this.extractList(services) as unknown as string[]);
        this.globalEnabled.set(!!(enabled as AnyRecord)?.['status']);
        this.cgnatEnabled.set(!!(cgnat as AnyRecord)?.['status']);
        this.loading.set(false);
      },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.loading.set(false); },
    });
  }

  toggleGlobal(value: boolean): void {
    this.dyndns.setGlobalEnable({ enable: value }).subscribe({
      next: () => this.globalEnabled.set(value),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  toggleCgnat(value: boolean): void {
    this.dyndns.setEnableOnCgnat({ enable: value }).subscribe({
      next: () => this.cgnatEnabled.set(value),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  addHost(): void {
    if (this.addForm.invalid) return;
    this.saving.set(true);
    this.dyndns.addHost(this.addForm.value as unknown as DynDNSHostCreate).subscribe({
      next: () => {
        this.saving.set(false);
        this.showAddForm.set(false);
        this.addForm.reset({ enable: true });
        this.reloadHosts();
      },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.saving.set(false); },
    });
  }

  confirmDelete(hostname: string): void { this.deleteTarget.set(hostname); }

  deleteHost(): void {
    const hostname = this.deleteTarget();
    if (!hostname) return;
    this.deleteTarget.set(null);
    this.dyndns.deleteHost(hostname).subscribe({
      next: () => this.reloadHosts(),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  private reloadHosts(): void {
    this.dyndns.getHosts().subscribe({
      next: (data) => this.hosts.set(this.extractList(data)),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
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
}
