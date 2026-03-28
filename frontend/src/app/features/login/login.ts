import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth.service';
import { TranslationService } from '../../core/i18n/translation.service';
import { TranslatePipe } from '../../core/i18n/translate.pipe';
import { ErrorResponse } from '../../models';

@Component({
  selector: 'app-login',
  templateUrl: './login.html',
  styleUrl: './login.css',
  imports: [TranslatePipe],
})
export default class Login {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly i18n = inject(TranslationService);

  readonly url = signal('http://192.168.1.1');
  readonly username = signal('');
  readonly password = signal('');
  readonly error = signal<string | null>(null);
  readonly loading = signal(false);

  submit(): void {
    this.error.set(null);
    this.loading.set(true);
    this.auth.login(this.url(), this.username(), this.password()).subscribe({
      next: () => this.router.navigate(['/devices']),
      error: (e: ErrorResponse) => {
        this.error.set(e.detail ?? this.i18n.t('login.failed'));
        this.loading.set(false);
      },
    });
  }
}
