import { Component, inject, signal, OnInit } from '@angular/core';
import { JsonPipe } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { LanService } from '../../services/lan.service';
import { ErrorResponse } from '../../models';
import { LoadingSpinner } from '../../shared/loading-spinner/loading-spinner';
import { ErrorBanner } from '../../shared/error-banner/error-banner';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecord = Record<string, any>;

@Component({
  selector: 'app-lan',
  templateUrl: './lan.html',
  styleUrl: './lan.css',
  imports: [ReactiveFormsModule, JsonPipe, LoadingSpinner, ErrorBanner],
})
export default class Lan implements OnInit {
  private readonly lan = inject(LanService);
  private readonly fb = inject(FormBuilder);

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly monitoring = signal(false);

  readonly wanCounters = signal<AnyRecord | null>(null);
  readonly saturation = signal<AnyRecord | null>(null);
  readonly interfaces = signal<string[]>([]);
  readonly statsResult = signal<AnyRecord | null>(null);
  readonly statsLoading = signal(false);

  readonly statsForm = this.fb.group({
    seconds: [60, Validators.required],
    numberOfReadings: [5, Validators.required],
    interfaceNames: ['', Validators.required],
  });

  readonly monitorForm = this.fb.group({
    duration: [60, Validators.required],
    interval: [5, Validators.required],
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.lan.getWANCounters().subscribe({
      next: (d) => { this.wanCounters.set(d as AnyRecord); this.loading.set(false); },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.loading.set(false); },
    });
    this.lan.getSaturationResults().subscribe({
      next: (d) => this.saturation.set(d as AnyRecord),
    });
    this.lan.getInterfacesNames().subscribe({
      next: (d) => {
        const list = this.extractList(d);
        this.interfaces.set(list.map((i: AnyRecord) => String(i['name'] ?? i)));
      },
    });
  }

  runStats(): void {
    if (this.statsForm.invalid) return;
    const v = this.statsForm.value;
    this.statsLoading.set(true);
    this.lan.getStats({
      seconds: Number(v.seconds),
      numberOfReadings: Number(v.numberOfReadings),
      interfaceNames: String(v.interfaceNames).split(',').map((s) => s.trim()),
    }).subscribe({
      next: (d) => { this.statsResult.set(d as AnyRecord); this.statsLoading.set(false); },
      error: (err: ErrorResponse) => { this.error.set(err.detail); this.statsLoading.set(false); },
    });
  }

  startMonitoring(): void {
    if (this.monitorForm.invalid) return;
    const v = this.monitorForm.value;
    this.lan.startInterfaceMonitoring({ duration: Number(v.duration), interval: Number(v.interval) })
      .subscribe({
        next: () => this.monitoring.set(true),
        error: (err: ErrorResponse) => this.error.set(err.detail),
      });
  }

  stopMonitoring(): void {
    this.lan.stopInterfaceMonitoring().subscribe({
      next: () => this.monitoring.set(false),
      error: (err: ErrorResponse) => this.error.set(err.detail),
    });
  }

  entries(obj: AnyRecord | null): [string, unknown][] {
    if (!obj) return [];
    const d = obj['data'] ?? obj['status'] ?? obj;
    if (typeof d === 'object' && d !== null) return Object.entries(d as AnyRecord);
    return [];
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
