import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from '@core/guards/auth.guard';
import { TimesheetComponent } from './pages/timesheet/timesheet.component';
import { TimesheetAutomationComponent } from './pages/timesheet-automation/timesheet-automation.component';
import { ValidationTimesheetComponent } from './pages/validation-timesheet/validation-timesheet.component';
import { UserTimesheetsListComponent } from './pages/user-timesheets-list/user-timesheets-list.component';
import { UserTimesheetsComponent } from './pages/user-timesheets/user-timesheets.component';

const routes: Routes = [
  { path: 'timesheet/:id', component: TimesheetComponent },
  { path: 'timesheet', component: TimesheetAutomationComponent, canActivate: [AuthGuard], data: { roles: ['user', 'Admin'] } },
  { path: 'user-timesheets-list', component: UserTimesheetsListComponent },
  { path: 'user-timesheet/:userProjectId/:projectId', component: UserTimesheetsListComponent },
  { path: 'validation-timesheet', component: ValidationTimesheetComponent, canActivate: [AuthGuard], data: { roles: ['user', 'Admin'] } }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class TimesheetsRoutingModule { }
