import { NgApexchartsModule } from 'ng-apexcharts';
import { SharedModule } from '@shared/shared.module';
import { CoreModule } from '@core/core.module';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AttendanceRoutingModule } from './attendance-routing.module';
import { AttendanceDashboardComponent } from './pages/attendance-dashboard/attendance-dashboard.component';

@NgModule({
  declarations: [
    AttendanceDashboardComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    AttendanceRoutingModule,
    CoreModule,
    SharedModule,
    NgApexchartsModule
  ]
})
export class AttendanceModule { }
