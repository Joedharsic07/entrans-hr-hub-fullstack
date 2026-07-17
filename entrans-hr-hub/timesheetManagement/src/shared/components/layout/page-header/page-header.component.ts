import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-page-header',
  templateUrl: './page-header.component.html'
})
export class PageHeaderComponent {
  @Input() pageTitle: string = '';
  @Input() pageSubtitle?: string;
  @Input() breadcrumbs?: { label: string; active?: boolean }[] = [];
}
