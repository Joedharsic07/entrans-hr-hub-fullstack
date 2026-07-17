import { AnalyticsModule } from '@features/analytics/analytics.module';
import { NgApexchartsModule } from 'ng-apexcharts';
import { SharedModule } from '@shared/shared.module';
import { CoreModule } from '@core/core.module';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AdminRoutingModule } from './admin-routing.module';
import { AdminComponent } from './pages/admin/admin.component';
import { CreateUserComponent } from './pages/create-user/create-user.component';
import { UserListComponent } from './pages/user-list/user-list.component';
import { PptAutomationComponent } from './pages/ppt-automation/ppt-automation.component';

@NgModule({
  declarations: [
    AdminComponent,
    CreateUserComponent,
    UserListComponent,
    PptAutomationComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    AdminRoutingModule,
    CoreModule,
    SharedModule,
    NgApexchartsModule,
    AnalyticsModule
  ]
})
export class AdminModule { }
