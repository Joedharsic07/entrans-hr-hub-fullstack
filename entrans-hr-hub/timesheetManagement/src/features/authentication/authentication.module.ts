import { NgApexchartsModule } from 'ng-apexcharts';
import { SharedModule } from '@shared/shared.module';
import { CoreModule } from '@core/core.module';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AuthenticationRoutingModule } from './authentication-routing.module';
import { LoginComponent } from './pages/login/login.component';
import { SignupComponent } from './pages/signup/signup.component';
import { ResetPasswordComponent } from './pages/reset-password/reset-password.component';
import { ConfrimResetPasswordComponent } from './pages/confrim-reset-password/confrim-reset-password.component';

@NgModule({
  declarations: [
    LoginComponent,
    SignupComponent,
    ResetPasswordComponent,
    ConfrimResetPasswordComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    AuthenticationRoutingModule,
    CoreModule,
    SharedModule,
    NgApexchartsModule
  ]
})
export class AuthenticationModule { }
