import { Injectable, signal } from '@angular/core';

const BREAKPOINT = '(min-width: 1024px)';

@Injectable({ providedIn: 'root' })
export class LayoutService {
  private readonly mq: MediaQueryList | null =
    typeof window !== 'undefined' ? window.matchMedia(BREAKPOINT) : null;

  readonly sidebarOpen = signal(this.mq?.matches ?? true);

  constructor() {
    this.mq?.addEventListener('change', (e) => this.sidebarOpen.set(e.matches));
  }

  toggle(): void { this.sidebarOpen.update((v) => !v); }
}
