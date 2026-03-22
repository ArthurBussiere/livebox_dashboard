import { Component, input, output } from '@angular/core';

@Component({
  selector: 'app-error-banner',
  template: `
    @if (message()) {
      <div class="error-banner" role="alert">
        <span class="error-banner__text">{{ message() }}</span>
        <button class="error-banner__close" (click)="dismissed.emit()" aria-label="Dismiss">✕</button>
      </div>
    }
  `,
  styleUrl: './error-banner.css',
})
export class ErrorBanner {
  readonly message = input<string | null>(null);
  readonly dismissed = output<void>();
}
