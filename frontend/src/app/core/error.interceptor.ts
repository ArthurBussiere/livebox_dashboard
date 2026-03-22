import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { Router } from '@angular/router';
import { NotificationService } from './notification.service';
import { AuthService } from './auth.service';
import { ErrorResponse } from '../models';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  // inject() must be called in the injection context (interceptor setup), not inside catchError
  const notifications = inject(NotificationService);
  const auth = inject(AuthService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status === 401 && !req.url.includes('/auth/login')) {
        auth.clearToken();
        router.navigate(['/login']);
        return throwError(() => ({ detail: 'Session expired', code: 401 }) as ErrorResponse);
      }

      const error: ErrorResponse =
        err.error?.detail != null
          ? (err.error as ErrorResponse)
          : { detail: err.message, code: err.status };

      notifications.error(error.detail);
      return throwError(() => error);
    }),
  );
};
