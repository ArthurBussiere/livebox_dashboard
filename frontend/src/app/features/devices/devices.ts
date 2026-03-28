import { Component, inject, signal, computed, effect, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TranslationService } from '../../core/i18n/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { DevicesService } from '../../services/devices.service';
import { DeviceRegistryService } from '../../core/device-registry.service';
import { ErrorResponse } from '../../models';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { ErrorBanner } from '../../shared/error-banner/error-banner';
import { StatusBadge } from '../../shared/status-badge/status-badge';
import { ConfirmDialog } from '../../shared/confirm-dialog/confirm-dialog';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>;

@Component({
  selector: 'app-devices',
  templateUrl: './devices.html',
  styleUrl: './devices.css',
  imports: [FormsModule, LoadingSpinner, ErrorBanner, StatusBadge, ConfirmDialog, TranslatePipe],
})
export default class Devices implements OnInit {
  private readonly devicesService = inject(DevicesService);
  private readonly registry = inject(DeviceRegistryService);
  readonly i18n = inject(TranslationService);

  readonly loading = computed(() => this.registry.loading());
  readonly error = signal<string | null>(null);
  readonly allDevices = signal<AnyRecord[]>([]);
  readonly search = signal('');
  readonly statusFilter = signal<'all' | 'active' | 'inactive'>('all');
  readonly typeFilter = signal('');
  readonly deleteTarget = signal<AnyRecord | null>(null);

  readonly deviceTypes = computed(() => {
    const types = new Set(this.allDevices().map((d) => d['DeviceType']).filter(Boolean));
    return Array.from(types).sort();
  });

  readonly filtered = computed(() => {
    const q = this.search().toLowerCase();
    const status = this.statusFilter();
    const type = this.typeFilter();
    return this.allDevices().filter((d) => {
      if (!d['PhysAddress']) return false;
      if (status === 'active' && !d['Active']) return false;
      if (status === 'inactive' && d['Active']) return false;
      if (type && d['DeviceType'] !== type) return false;
      if (!q) return true;
      return [this.getDisplayName(d), d['IPAddress'], d['PhysAddress'], d['DeviceType']]
        .some((v) => String(v ?? '').toLowerCase().includes(q));
    });
  });

  constructor() {
    effect(() => {
      const list = this.registry.allDevices();
      if (this.registry.loaded()) this.allDevices.set(list);
    });
    effect(() => {
      const err = this.registry.error();
      if (err) this.error.set(err);
    });
  }

  ngOnInit(): void {
    // If registry already loaded (e.g. navigating back), no extra request needed
    if (!this.registry.loaded()) this.load();
  }

  load(): void {
    this.registry.load();
  }

  getDisplayName(device: AnyRecord): string {
    const names: AnyRecord[] = device['Names'] ?? [];
    const gui = names.find((n: AnyRecord) => n['Source'] === 'GUI');
    return gui ? gui['Name'] : (device['Name'] ?? '');
  }

  deleteMsg(): string {
    const t = this.deleteTarget();
    return this.i18n.t('devices.removeMsg', t?.['Name'] || t?.['IPAddress'] || this.i18n.t('devices.thisDevice'));
  }

  confirmDelete(device: AnyRecord): void { this.deleteTarget.set(device); }

  deleteDevice(): void {
    const target = this.deleteTarget();
    if (!target) return;
    this.deleteTarget.set(null);
    this.devicesService.destroyDevice(target['Key']).subscribe({
      next: () => this.allDevices.update((list) => list.filter((d) => d['Key'] !== target['Key'])),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }
}
