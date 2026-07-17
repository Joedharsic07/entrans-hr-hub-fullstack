import { NgApexchartsModule } from 'ng-apexcharts';
import { SharedModule } from '@shared/shared.module';
import { CoreModule } from '@core/core.module';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ProjectsRoutingModule } from './projects-routing.module';
import { CreateProjectComponent } from './pages/create-project/create-project.component';
import { ProjectMembersComponent } from './pages/project-members/project-members.component';

@NgModule({
  declarations: [
    CreateProjectComponent,
    ProjectMembersComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    ProjectsRoutingModule,
    CoreModule,
    SharedModule,
    NgApexchartsModule
  ]
})
export class ProjectsModule { }
