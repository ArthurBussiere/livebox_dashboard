import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../core/api.service';

@Injectable({ providedIn: 'root' })
export class PhoneService {
  private readonly api = inject(ApiService);

  getConfig(): Observable<unknown> {
    return this.api.get('/phone/config');
  }

  getInfo(): Observable<unknown> {
    return this.api.get('/phone/info');
  }
}
