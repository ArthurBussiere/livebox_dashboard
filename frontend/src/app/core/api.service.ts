import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { catchError, Observable, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { ErrorResponse } from '../models';

type ParamValue = string | number | boolean | string[];

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  get<T>(path: string, params?: Record<string, ParamValue | undefined>): Observable<T> {
    return this.http
      .get<T>(`${this.base}${path}`, { params: this.toParams(params) })
      .pipe(catchError(this.handleError));
  }

  post<T>(path: string, body: unknown = {}): Observable<T> {
    return this.http
      .post<T>(`${this.base}${path}`, body)
      .pipe(catchError(this.handleError));
  }

  put<T>(path: string, body: unknown): Observable<T> {
    return this.http
      .put<T>(`${this.base}${path}`, body)
      .pipe(catchError(this.handleError));
  }

  patch<T>(path: string, body: unknown): Observable<T> {
    return this.http
      .patch<T>(`${this.base}${path}`, body)
      .pipe(catchError(this.handleError));
  }

  delete<T>(path: string, params?: Record<string, ParamValue | undefined>): Observable<T> {
    return this.http
      .delete<T>(`${this.base}${path}`, { params: this.toParams(params) })
      .pipe(catchError(this.handleError));
  }

  deleteWithBody<T>(path: string, body: unknown): Observable<T> {
    return this.http
      .delete<T>(`${this.base}${path}`, { body })
      .pipe(catchError(this.handleError));
  }

  private toParams(obj?: Record<string, ParamValue | undefined>): HttpParams {
    let params = new HttpParams();
    if (!obj) return params;
    for (const [key, value] of Object.entries(obj)) {
      if (value === undefined || value === null) continue;
      if (Array.isArray(value)) {
        value.forEach((v) => (params = params.append(key, v)));
      } else {
        params = params.set(key, String(value));
      }
    }
    return params;
  }

  private handleError(err: HttpErrorResponse): Observable<never> {
    const error: ErrorResponse =
      err.error?.detail != null
        ? (err.error as ErrorResponse)
        : { detail: err.message, code: err.status };
    return throwError(() => error);
  }
}
