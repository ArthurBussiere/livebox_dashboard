import { Component, inject, signal, OnInit } from '@angular/core';
import { ReactiveFormsModule, FormsModule, FormBuilder, Validators } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { FirewallService } from '../../services/firewall.service';
import { DeviceRegistryService } from '../../core/device-registry.service';
import { NotificationService } from '../../core/notification.service';
import { ErrorResponse, FirewallLevel, Protocol } from '../../models';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { ErrorBanner } from '../../shared/error-banner/error-banner';
import { StatusBadge } from '../../shared/status-badge/status-badge';
import { ConfirmDialog } from '../../shared/confirm-dialog/confirm-dialog';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>;

type FwTab = 'level' | 'portforwarding' | 'dmz';

@Component({
  selector: 'app-firewall',
  templateUrl: './firewall.html',
  styleUrl: './firewall.css',
  imports: [ReactiveFormsModule, FormsModule, LoadingSpinner, ErrorBanner, StatusBadge, ConfirmDialog],
})
export default class Firewall implements OnInit {
  private readonly fw = inject(FirewallService);
  private readonly fb = inject(FormBuilder);
  private readonly notify = inject(NotificationService);
  readonly registry = inject(DeviceRegistryService);

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly saving = signal(false);
  readonly tab = signal<FwTab>('portforwarding');

  readonly ipv4Level = signal<FirewallLevel>('Medium');
  readonly ipv6Level = signal<FirewallLevel>('Medium');
  readonly portRules = signal<AnyRecord[]>([]);
  readonly dmzRules = signal<AnyRecord[]>([]);

  readonly showPortForm = signal(false);
  readonly showDmzForm = signal(false);
  readonly deleteTarget = signal<{ type: string; item: AnyRecord } | null>(null);

  readonly levels: FirewallLevel[] = ['Low', 'Medium', 'High', 'Custom'];
  readonly protocols: Protocol[] = ['TCP', 'UDP', 'TCP,UDP'];

  private static readonly PROTO_TO_NUM: Record<string, string> = { TCP: '6', UDP: '17' };
  private static readonly NUM_TO_PROTO: Record<string, string> = { '6': 'TCP', '17': 'UDP' };

  protoNum(p: string): string {
    return Firewall.PROTO_TO_NUM[p] ?? p;
  }

  protoLabel(p: string | undefined): string {
    if (!p) return '—';
    return Firewall.NUM_TO_PROTO[p] ?? p;
  }

  readonly portForm = this.fb.group({
    internalPort: [80, [Validators.required, Validators.min(1)]],
    externalPort: [null as number | null],
    destinationIpAddress: ['', Validators.required],
    protocol: ['TCP' as Protocol, Validators.required],
    description: [''],
    enable: [true],
    persistent: [true],
  });

  readonly dmzForm = this.fb.group({
    sourceInterface: ['', Validators.required],
    destinationIpAddress: ['', Validators.required],
    enable: [true],
    sourcePrefix: [''],
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    forkJoin({
      level: this.fw.getLevel(),
      ipv6level: this.fw.getIPv6Level(),
      port: this.fw.getPortForwarding(),
      dmz: this.fw.getDMZ(),
    }).subscribe({
      next: ({ level, ipv6level, port, dmz }) => {
        this.ipv4Level.set((this.extract(level)?.['Level'] as FirewallLevel) ?? 'Medium');
        this.ipv6Level.set((this.extract(ipv6level)?.['Level'] as FirewallLevel) ?? 'Medium');
        this.portRules.set(this.extractList(port));
        this.dmzRules.set(this.extractList(dmz));
        this.loading.set(false);
      },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.loading.set(false); },
    });
  }

  saveLevel(): void {
    this.saving.set(true);
    forkJoin({
      v4: this.fw.setLevel({ level: this.ipv4Level() }),
      v6: this.fw.setIPv6Level({ level: this.ipv6Level() }),
    }).subscribe({
      next: () => {
        this.saving.set(false);
        this.fw.commit().subscribe({
          next: () => this.notify.success('Niveau de pare-feu appliqué avec succès.'),
          error: () => this.notify.success('Niveau de pare-feu appliqué (commit non confirmé).'),
        });
      },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.saving.set(false); },
    });
  }

  addPortRule(): void {
    if (this.portForm.invalid) return;
    this.saving.set(true);
    const v = this.portForm.value;
    this.fw.createPortForwarding({
      origin: 'webui', sourceInterface: 'data',
      internalPort: String(v.internalPort!), destinationIPAddress: v.destinationIpAddress!,
      protocol: this.protoNum(v.protocol!) as Protocol,
      externalPort: v.externalPort != null ? String(v.externalPort) : undefined,
      description: v.description || undefined,
      enable: !!v.enable, persistent: !!v.persistent,
    }).subscribe({
      next: () => {
        this.saving.set(false); this.showPortForm.set(false); this.portForm.reset({ internalPort: 80, protocol: 'TCP', enable: true, persistent: true });
        this.notify.success('Règle de port forwarding ajoutée.');
        this.reloadRules('port');
      },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.saving.set(false); },
    });
  }

  addDmzRule(): void {
    if (this.dmzForm.invalid) return;
    this.saving.set(true);
    const v = this.dmzForm.value;
    this.fw.createDMZ({
      sourceInterface: v.sourceInterface!, destinationIPAddress: v.destinationIpAddress!,
      enable: !!v.enable, sourcePrefix: v.sourcePrefix || undefined,
    }).subscribe({
      next: () => { this.saving.set(false); this.showDmzForm.set(false); this.dmzForm.reset({ enable: true }); this.reloadRules('dmz'); },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.saving.set(false); },
    });
  }

  togglePortRule(r: AnyRecord): void {
    const id = String(r['Id'] ?? '');
    const enable = !r['Enable'];
    this.fw.enablePortForwarding(id, { origin: r['Origin'] ?? 'webui', enable }).subscribe({
      next: () => {
        this.portRules.update((rules) => rules.map((x) => x['Id'] === r['Id'] ? { ...x, Enable: enable } : x));
        this.notify.success(enable ? 'Règle activée.' : 'Règle désactivée.');
      },
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  confirmDelete(type: string, item: AnyRecord): void { this.deleteTarget.set({ type, item }); }

  deleteRule(): void {
    const t = this.deleteTarget();
    if (!t) return;
    this.deleteTarget.set(null);
    const id = String(t.item['Id'] ?? t.item['id'] ?? '');
    const obs = t.type === 'port'
      ? this.fw.deletePortForwarding(id, t.item['Origin'] ?? '')
      : this.fw.deleteDMZ(id);
    obs.subscribe({
      next: () => {
        this.notify.success('Règle supprimée.');
        this.reloadRules(t.type);
      },
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  private reloadRules(type: string): void {
    if (type === 'port') this.fw.getPortForwarding().subscribe({ next: (d) => this.portRules.set(this.extractList(d)) });
    else if (type === 'dmz') this.fw.getDMZ().subscribe({ next: (d) => this.dmzRules.set(this.extractList(d)) });
  }

  private extractList(data: unknown): AnyRecord[] {
    const r = data as AnyRecord;
    const inner = r?.['data'] ?? r?.['status'] ?? r;
    if (Array.isArray(inner)) return inner;
    if (typeof inner === 'object' && inner !== null) {
      const values = Object.values(inner as AnyRecord);
      const first = values[0];
      if (Array.isArray(first)) return first;
      if (values.length > 0 && values.every((v) => typeof v === 'object' && v !== null)) {
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
