import { Injectable, signal } from '@angular/core';

export interface Toast {
  id: number;
  type: 'error' | 'success' | 'info';
  message: string;
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  readonly toasts = signal<Toast[]>([]);

  private nextId = 0;

  error(message: string, duration = 6000): void {
    this.add('error', message, duration);
  }

  success(message: string, duration = 3500): void {
    this.add('success', message, duration);
  }

  info(message: string, duration = 3500): void {
    this.add('info', message, duration);
  }

  dismiss(id: number): void {
    this.toasts.update((list) => list.filter((t) => t.id !== id));
  }

  private add(type: Toast['type'], message: string, duration: number): void {
    const id = this.nextId++;
    this.toasts.update((list) => [...list, { id, type, message }]);
    if (duration > 0) {
      setTimeout(() => this.dismiss(id), duration);
    }
  }
}
