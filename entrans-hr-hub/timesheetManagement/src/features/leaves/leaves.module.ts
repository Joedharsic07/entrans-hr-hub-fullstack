import { NgApexchartsModule } from 'ng-apexcharts';
import { SharedModule } from '@shared/shared.module';
import { CoreModule } from '@core/core.module';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { LeavesRoutingModule } from './leaves-routing.module';
import { LeaveDashboardComponent } from './pages/leave-dashboard/leave-dashboard.component';

@NgModule({
  declarations: [
    LeaveDashboardComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    LeavesRoutingModule,
    CoreModule,
    SharedModule,
    NgApexchartsModule
  ]
})
export class LeavesModule { }
