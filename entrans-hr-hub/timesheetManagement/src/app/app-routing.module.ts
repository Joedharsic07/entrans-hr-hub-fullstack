import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  {
    path: '',
    loadChildren: () => import('@features/authentication/authentication.module').then(m => m.AuthenticationModule)
  },
  {
    path: '',
    loadChildren: () => import('@features/admin/admin.module').then(m => m.AdminModule)
  },
  {
    path: '',
    loadChildren: () => import('@features/analytics/analytics.module').then(m => m.AnalyticsModule)
  },
  {
    path: '',
    loadChildren: () => import('@features/attendance/attendance.module').then(m => m.AttendanceModule)
  },
  {
    path: '',
    loadChildren: () => import('@features/leaves/leaves.module').then(m => m.LeavesModule)
  },
  {
    path: '',
    loadChildren: () => import('@features/profile/profile.module').then(m => m.ProfileModule)
  },
  {
    path: '',
    loadChildren: () => import('@features/projects/projects.module').then(m => m.ProjectsModule)
  },
  {
    path: '',
    loadChildren: () => import('@features/timesheets/timesheets.module').then(m => m.TimesheetsModule)
  },
  { path: '**', redirectTo: 'login', pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
