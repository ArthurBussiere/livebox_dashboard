import { Injectable, signal, effect } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  readonly dark = signal<boolean>(localStorage.getItem('theme') === 'dark');

  constructor() {
    effect(() => {
      document.documentElement.setAttribute('data-theme', this.dark() ? 'dark' : 'light');
    });
    document.documentElement.setAttribute('data-theme', this.dark() ? 'dark' : 'light');
  }

  toggle(): void {
    const next = !this.dark();
    this.dark.set(next);
    localStorage.setItem('theme', next ? 'dark' : 'light');
  }
}
