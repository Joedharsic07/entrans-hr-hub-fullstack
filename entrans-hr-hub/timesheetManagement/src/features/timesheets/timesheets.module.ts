import { NgApexchartsModule } from 'ng-apexcharts';
import { SharedModule } from '@shared/shared.module';
import { CoreModule } from '@core/core.module';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TimesheetsRoutingModule } from './timesheets-routing.module';
import { TimesheetComponent } from './pages/timesheet/timesheet.component';
import { TimesheetAutomationComponent } from './pages/timesheet-automation/timesheet-automation.component';
import { ValidationTimesheetComponent } from './pages/validation-timesheet/validation-timesheet.component';
import { UserTimesheetsListComponent } from './pages/user-timesheets-list/user-timesheets-list.component';
import { UserTimesheetsComponent } from './pages/user-timesheets/user-timesheets.component';

@NgModule({
  declarations: [
    TimesheetComponent,
    TimesheetAutomationComponent,
    ValidationTimesheetComponent,
    UserTimesheetsListComponent,
    UserTimesheetsComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    TimesheetsRoutingModule,
    CoreModule,
    SharedModule,
    NgApexchartsModule
  ]
})
export class TimesheetsModule { }
