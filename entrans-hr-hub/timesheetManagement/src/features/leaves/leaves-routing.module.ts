import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from '@core/guards/auth.guard';
import { LeaveDashboardComponent } from './pages/leave-dashboard/leave-dashboard.component';

const routes: Routes = [
  { path: 'leaves', component: LeaveDashboardComponent, canActivate: [AuthGuard] }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class LeavesRoutingModule { }
