import { Component, input, output } from '@angular/core';

@Component({
  selector: 'app-confirm-dialog',
  templateUrl: './confirm-dialog.html',
  styleUrl: './confirm-dialog.css',
})
export class ConfirmDialog {
  readonly open = input(false);
  readonly title = input('Confirm');
  readonly message = input('Are you sure?');
  readonly confirmLabel = input('Confirm');
  readonly danger = input(false);
  readonly confirmed = output<void>();
  readonly cancelled = output<void>();
}
