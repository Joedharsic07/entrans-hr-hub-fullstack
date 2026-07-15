import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { NgApexchartsModule } from 'ng-apexcharts';
import { SharedModule } from './shared/shared.module';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './component/login/login.component';
import { SignupComponent } from './component/signup/signup.component';
import { TimesheetComponent } from './timesheet/timesheet/timesheet.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HTTP_INTERCEPTORS, HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import {  AuthInterceptorService } from './shared/interceptor/auth.interceptor';
import { ToastrModule } from 'ngx-toastr';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AdminComponent } from './Admin/admin/admin.component';
import { TimesheetAutomationComponent } from './Admin/timesheetauto/timesheet-automation/timesheet-automation.component';
import { PptAutomationComponent } from './Admin/ppt-automation/ppt-automation.component';
import { SidebarComponent } from './Admin/sidebar/sidebar.component';
import { AuthGuard } from './shared/Auth/auth.guard';
import { ResetPasswordComponent } from './component/reset-password/reset-password.component';
import { ConfrimResetPasswordComponent } from './component/confrim-reset-password/confrim-reset-password.component';
import { UserProfileComponent } from './component/user-profile/user-profile.component';
import { UserTimesheetsListComponent } from './Admin/user-timesheets-list/user-timesheets-list.component';
import { CreateProjectComponent } from './Admin/create-project/create-project.component';
import { ValidationTimesheetComponent } from './Admin/validation-timesheet/validation-timesheet.component';
import { ProjectMembersComponent } from './Admin/project-members/project-members.component';
import { CreateUserComponent } from './Admin/create-user/create-user.component';
import { UserListComponent } from './Admin/user-list/user-list.component';
import { FooterComponent } from './Admin/footer/footer.component';
import { LeaveDashboardComponent } from './component/leave-dashboard/leave-dashboard.component';
import { AttendanceDashboardComponent } from './component/attendance-dashboard/attendance-dashboard.component';
import { AnalyticsDashboardComponent } from './Admin/analytics-dashboard/analytics-dashboard.component';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    SignupComponent,
    TimesheetComponent,
    AdminComponent,
    TimesheetAutomationComponent,
    PptAutomationComponent,
    SidebarComponent,
    ResetPasswordComponent,
    ConfrimResetPasswordComponent,
    UserProfileComponent,
    UserTimesheetsListComponent,
    CreateProjectComponent,
    ValidationTimesheetComponent,
    ProjectMembersComponent,
    CreateUserComponent,
    UserListComponent,
    FooterComponent,
    LeaveDashboardComponent,
    AttendanceDashboardComponent,
    AnalyticsDashboardComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    CommonModule,
    ReactiveFormsModule,
    HttpClientModule ,
    ToastrModule.forRoot({ positionClass: 'toast-top-right', timeOut: 3000, preventDuplicates: true}),
    BrowserAnimationsModule,
    NgApexchartsModule,
    SharedModule
  ],
  providers: [{ provide: HTTP_INTERCEPTORS, useClass: AuthInterceptorService, multi: true,},AuthGuard

],
  bootstrap: [AppComponent]
})
export class AppModule { }
