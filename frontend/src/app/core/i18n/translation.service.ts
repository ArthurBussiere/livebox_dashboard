import { Injectable, signal } from '@angular/core';
import { Lang, TranslationKey, translations } from './translations';

@Injectable({ providedIn: 'root' })
export class TranslationService {
  readonly lang = signal<Lang>((localStorage.getItem('lang') as Lang) ?? 'en');

  toggle(): void {
    const next: Lang = this.lang() === 'en' ? 'fr' : 'en';
    this.lang.set(next);
    localStorage.setItem('lang', next);
  }

  t(key: TranslationKey, ...params: string[]): string {
    let result: string = translations[this.lang()][key] ?? key;
    params.forEach((p, i) => { result = result.replace(`{${i}}`, p); });
    return result;
  }
}
