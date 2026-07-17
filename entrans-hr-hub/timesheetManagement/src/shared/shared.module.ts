import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NotificationCenterComponent } from './components/notification-center/notification-center.component';
import { GlobalSearchComponent } from './components/global-search/global-search.component';
import { ActivityTimelineComponent } from './components/activity-timeline/activity-timeline.component';
import { PageContainerComponent } from './components/layout/page-container/page-container.component';
import { PageHeaderComponent } from './components/layout/page-header/page-header.component';
import { CoreModule } from '../core/core.module';

@NgModule({
  declarations: [
    NotificationCenterComponent,
    GlobalSearchComponent,
    ActivityTimelineComponent,
    PageContainerComponent,
    PageHeaderComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    CoreModule
  ],
  exports: [
    NotificationCenterComponent,
    GlobalSearchComponent,
    ActivityTimelineComponent,
    PageContainerComponent,
    PageHeaderComponent
  ]
})
export class SharedModule { }
