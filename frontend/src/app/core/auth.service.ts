import { computed, inject, Injectable, PLATFORM_ID, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { map, Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly platformId = inject(PLATFORM_ID);
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly TOKEN_KEY = 'livebox_token';
  private readonly base = environment.apiUrl;

  readonly token = signal<string | null>(
    isPlatformBrowser(this.platformId) ? localStorage.getItem(this.TOKEN_KEY) : null,
  );
  readonly isAuthenticated = computed(() => this.token() !== null);

  login(url: string, username: string, password: string): Observable<void> {
    return this.http
      .post<{ token: string }>(`${this.base}/auth/login`, { url, username, password })
      .pipe(
        tap(({ token }) => this.setToken(token)),
        map(() => void 0),
      );
  }

  logout(): void {
    const token = this.token();
    this.clearToken();
    this.router.navigate(['/login']);
    if (token) {
      this.http
        .post(`${this.base}/auth/logout`, {}, {
          headers: { Authorization: `Bearer ${token}` },
        })
        .subscribe({ error: () => {} });
    }
  }

  setToken(token: string): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem(this.TOKEN_KEY, token);
    }
    this.token.set(token);
  }

  clearToken(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem(this.TOKEN_KEY);
    }
    this.token.set(null);
  }
}
