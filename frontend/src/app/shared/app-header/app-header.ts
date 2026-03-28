import { Component, inject, computed, effect } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { map, catchError, of } from 'rxjs';
import { WifiService } from '../../services/wifi.service';
import { NmcService } from '../../services/nmc.service';
import { DeviceRegistryService } from '../../core/device-registry.service';
import { LayoutService } from '../../core/layout.service';
import { AuthService } from '../../core/auth.service';
import { TranslationService } from '../../core/i18n/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { ThemeService } from '../../core/theme.service';
import { ErrorResponse } from '../../models';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>;

@Component({
  selector: 'app-header',
  templateUrl: './app-header.html',
  styleUrl: './app-header.css',
  imports: [TranslatePipe],
})
export class AppHeader {
  readonly i18n = inject(TranslationService);
  readonly theme = inject(ThemeService);
  private readonly registry = inject(DeviceRegistryService);
  private readonly wifiService = inject(WifiService);
  private readonly nmc = inject(NmcService);
  readonly layout = inject(LayoutService);
  readonly auth = inject(AuthService);

  readonly wanStatus = toSignal(
    this.nmc.getWANStatus().pipe(
      map((raw) => this.extract(raw)),
      catchError(() => of(null)),
    ),
  );

  private readonly wifiData = toSignal(
    this.wifiService.get().pipe(
      map((raw) => this.extract(raw)),
      catchError(() => of(null)),
    ),
  );

  readonly wifiEnabled = this.wifiService.wifiEnabled;
  readonly wifiSsid = computed(() => this.wifiData()?.['SSID'] as string | undefined);
  readonly wifiChannel = computed(() => this.wifiData()?.['Channel'] as string | undefined);

  readonly activeDevices = computed(() =>
    this.registry.allDevices().filter((d) => d['Active']).length,
  );
  readonly totalDevices = computed(() => this.registry.allDevices().length);

  constructor() {
    effect(() => {
      const data = this.wifiData();
      if (data != null) this.wifiService.wifiEnabled.set(!!data['Enable']);
    });
  }

  wanUp(): boolean {
    return String(this.wanStatus()?.['WanState'] ?? '').toLowerCase() === 'up';
  }

  toggleWifi(): void {
    this.wifiService.toggle().subscribe({
      error: (err: ErrorResponse) => { this.wifiService.revertEnabled(); console.error(err.detail); },
    });
  }

  private extract(raw: unknown): AnyRecord {
    const r = raw as AnyRecord;
    return (r?.['data'] ?? r?.['status'] ?? r) as AnyRecord;
  }
}
