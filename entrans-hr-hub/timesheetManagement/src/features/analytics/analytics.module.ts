import { NgApexchartsModule } from 'ng-apexcharts';
import { SharedModule } from '@shared/shared.module';
import { CoreModule } from '@core/core.module';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AnalyticsRoutingModule } from './analytics-routing.module';
import { AnalyticsDashboardComponent } from './pages/analytics-dashboard/analytics-dashboard.component';

@NgModule({
  declarations: [
    AnalyticsDashboardComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    AnalyticsRoutingModule,
    CoreModule,
    SharedModule,
    NgApexchartsModule
  ],
  exports: [
    AnalyticsDashboardComponent
  ]
})
export class AnalyticsModule { }
