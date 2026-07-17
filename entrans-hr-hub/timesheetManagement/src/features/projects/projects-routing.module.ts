import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from '@core/guards/auth.guard';
import { CreateProjectComponent } from './pages/create-project/create-project.component';
import { ProjectMembersComponent } from './pages/project-members/project-members.component';

const routes: Routes = [
  { path: 'create-project', component: CreateProjectComponent, canActivate: [AuthGuard], data: { roles: ['user', 'Admin'] } },
  { path: 'project-members', component: ProjectMembersComponent, canActivate: [AuthGuard], data: { roles: ['Admin'] } }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ProjectsRoutingModule { }
