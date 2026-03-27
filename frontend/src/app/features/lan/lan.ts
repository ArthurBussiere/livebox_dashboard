import { Component, inject, computed, OnInit, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { TrafficWsService, POLL_INTERVAL_S } from '../../services/traffic-ws.service';


const CHART_W = 800;
const CHART_H = 320;
const MAX_POINTS = 120; // must match MAX_HISTORY in traffic-ws.service

@Component({
  selector: 'app-lan',
  templateUrl: './lan.html',
  styleUrl: './lan.css',
  imports: [],
})
export default class Lan implements OnInit {
  private readonly trafficWs = inject(TrafficWsService);
  private readonly platformId = inject(PLATFORM_ID);

  /** History lives in the singleton service — persists across navigations. */
  readonly history = this.trafficWs.history;

  readonly chartW = CHART_W;
  readonly chartH = CHART_H;

  readonly currentRx = computed(() => {
    const h = this.history();
    return h.length ? h[h.length - 1].rxBps : 0;
  });
  readonly currentTx = computed(() => {
    const h = this.history();
    return h.length ? h[h.length - 1].txBps : 0;
  });
  readonly peakBps = computed(() => {
    const h = this.history();
    if (h.length === 0) return 1;
    const sorted = h.map(p => Math.max(p.rxBps, p.txBps)).sort((a, b) => a - b);
    const p95 = sorted[Math.floor(sorted.length * 0.95)] ?? sorted[sorted.length - 1];
    return Math.max(p95, 1);
  });
  readonly rxLinePath = computed(() => this.buildLinePath('rx'));
  readonly txLinePath = computed(() => this.buildLinePath('tx'));
  readonly rxAreaPath = computed(() => this.buildAreaPath('rx'));
  readonly txAreaPath = computed(() => this.buildAreaPath('tx'));
  readonly gridY25 = computed(() => (CHART_H * 0.25).toFixed(1));
  readonly gridY50 = computed(() => (CHART_H * 0.5).toFixed(1));
  readonly gridY75 = computed(() => (CHART_H * 0.75).toFixed(1));
  readonly labelPeak = computed(() => this.fmtBps(this.peakBps()));
  readonly labelHalf = computed(() => this.fmtBps(this.peakBps() / 2));
  readonly windowSeconds = computed(() => this.history().length * POLL_INTERVAL_S);

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      // Idempotent — only opens the WS if not already connected
      this.trafficWs.connect();
    }
  }

  private buildLinePath(type: 'rx' | 'tx'): string {
    const h = this.history();
    if (h.length < 2) return '';
    const max = this.peakBps();
    return h.map((p, i) => {
      const x = (i / (MAX_POINTS - 1)) * CHART_W;
      const val = type === 'rx' ? p.rxBps : p.txBps;
      const y = CHART_H - (val / max) * (CHART_H - 8);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(' ');
  }

  private buildAreaPath(type: 'rx' | 'tx'): string {
    const h = this.history();
    if (h.length < 2) return '';
    const max = this.peakBps();
    const pts = h.map((p, i) => {
      const x = (i / (MAX_POINTS - 1)) * CHART_W;
      const val = type === 'rx' ? p.rxBps : p.txBps;
      const y = CHART_H - (val / max) * (CHART_H - 8);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });
    const lastX = ((h.length - 1) / (MAX_POINTS - 1) * CHART_W).toFixed(1);
    return `0,${CHART_H} ${pts.join(' ')} ${lastX},${CHART_H}`;
  }

  fmtBps(bps: number): string {
    if (bps < 1024) return `${bps.toFixed(0)} B/s`;
    if (bps < 1024 * 1024) return `${(bps / 1024).toFixed(1)} KB/s`;
    return `${(bps / 1024 / 1024).toFixed(2)} MB/s`;
  }

}
