import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from '@core/guards/auth.guard';
import { AdminComponent } from './pages/admin/admin.component';
import { CreateUserComponent } from './pages/create-user/create-user.component';
import { UserListComponent } from './pages/user-list/user-list.component';
import { PptAutomationComponent } from './pages/ppt-automation/ppt-automation.component';

const routes: Routes = [
  { path: 'admin', component: AdminComponent },
  { path: 'create-user', component: CreateUserComponent, canActivate: [AuthGuard], data: { roles: ['Admin'] } },
  { path: 'user-list', component: UserListComponent, canActivate: [AuthGuard], data: { roles: ['Admin'] } },
  { path: 'ppt-automation', component: PptAutomationComponent, canActivate: [AuthGuard], data: { roles: ['user', 'Admin'] } }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdminRoutingModule { }
