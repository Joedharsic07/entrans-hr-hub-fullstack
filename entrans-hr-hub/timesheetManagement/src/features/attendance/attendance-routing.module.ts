import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from '@core/guards/auth.guard';
import { AttendanceDashboardComponent } from './pages/attendance-dashboard/attendance-dashboard.component';

const routes: Routes = [
  { path: 'attendance', component: AttendanceDashboardComponent, canActivate: [AuthGuard] }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AttendanceRoutingModule { }
