import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NotificationCenterComponent } from './notification-center/notification-center.component';
import { GlobalSearchComponent } from './global-search/global-search.component';
import { ActivityTimelineComponent } from './activity-timeline/activity-timeline.component';

@NgModule({
  declarations: [
    NotificationCenterComponent,
    GlobalSearchComponent,
    ActivityTimelineComponent
  ],
  imports: [
    CommonModule,
    FormsModule
  ],
  exports: [
    NotificationCenterComponent,
    GlobalSearchComponent,
    ActivityTimelineComponent
  ]
})
export class SharedModule { }
