import { Component, inject } from '@angular/core';
import { NotificationService, Toast } from '../../core/notification.service';

@Component({
  selector: 'app-toast',
  templateUrl: './toast.html',
  styleUrl: './toast.css',
})
export class ToastComponent {
  protected readonly notifications = inject(NotificationService);

  dismiss(id: number): void {
    this.notifications.dismiss(id);
  }

  trackById(_: number, toast: Toast): number {
    return toast.id;
  }
}
