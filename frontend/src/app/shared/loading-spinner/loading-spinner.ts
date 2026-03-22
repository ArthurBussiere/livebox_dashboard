import { Component } from '@angular/core';

@Component({
  selector: 'app-loading-spinner',
  template: `<div class="spinner" role="status" aria-label="Loading"></div>`,
  styleUrl: './loading-spinner.css',
})
export class LoadingSpinner {}
