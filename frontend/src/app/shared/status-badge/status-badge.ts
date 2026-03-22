import { Component, input } from '@angular/core';

@Component({
  selector: 'app-status-badge',
  template: `<span class="badge badge--{{ type() }}">{{ label() }}</span>`,
})
export class StatusBadge {
  readonly type = input<'success' | 'danger' | 'warning' | 'info' | 'muted'>('muted');
  readonly label = input('');
}
