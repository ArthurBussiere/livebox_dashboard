import { isPlatformBrowser } from '@angular/common';
import { effect, inject, Injectable, PLATFORM_ID, signal } from '@angular/core';
import { environment } from '../../environments/environment';
import { AuthService } from '../core/auth.service';

export interface TrafficPoint {
  rxBps: number;
  txBps: number;
  ts: number;
}

export const POLL_INTERVAL_S = 1;
const MAX_HISTORY = 120; // 2 minutes at 1 s/poll
const RECONNECT_DELAY_MS = 5_000;
const WS_PATH = '/ws/traffic';

@Injectable({ providedIn: 'root' })
export class TrafficWsService {
  private readonly auth = inject(AuthService);
  private readonly platformId = inject(PLATFORM_ID);

  private ws: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  private readonly _history = signal<TrafficPoint[]>([]);
  /** Read-only signal — persists across page navigations. */
  readonly history = this._history.asReadonly();

  constructor() {
    // Auto-disconnect and clear history when the user logs out
    effect(() => {
      if (!this.auth.token()) {
        this.disconnect();
      }
    });
  }

  /**
   * Open the WebSocket connection if not already open.
   * Safe to call multiple times (idempotent).
   */
  connect(): void {
    if (!isPlatformBrowser(this.platformId)) return;
    if (
      this.ws?.readyState === WebSocket.OPEN ||
      this.ws?.readyState === WebSocket.CONNECTING
    ) {
      return;
    }

    const token = this.auth.token();
    if (!token) return;

    const url = `${this.resolveWsBase()}${WS_PATH}?token=${token}`;

    this.ws = new WebSocket(url);

    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const point = JSON.parse(event.data as string) as TrafficPoint;
        this._history.update(h => {
          const next = [...h, point];
          return next.length > MAX_HISTORY ? next.slice(-MAX_HISTORY) : next;
        });
      } catch {
        // ignore malformed messages
      }
    };

    this.ws.onclose = () => {
      this.ws = null;
      // Auto-reconnect as long as the user is still authenticated
      if (this.auth.token()) {
        this.reconnectTimer = setTimeout(() => this.connect(), RECONNECT_DELAY_MS);
      }
    };

    this.ws.onerror = () => {
      // onclose will fire right after; reconnect logic is handled there
    };
  }

  /**
   * Derive the WebSocket base URL from environment.apiUrl so that both
   * HTTP and WS traffic go to the same host (no proxy mismatch).
   *
   * - Absolute URL (dev):  "http://localhost:4350/api" → "ws://localhost:4350/api"
   * - Relative URL (prod): "/api" → "ws://current-host/api"
   */
  private resolveWsBase(): string {
    const api = environment.apiUrl;
    if (api.startsWith('http')) {
      return api.replace(/^http/, 'ws');
    }
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${location.host}${api}`;
  }

  /** Close the connection and clear history (call on logout). */
  disconnect(): void {
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.ws?.close();
    this.ws = null;
    this._history.set([]);
  }
}
