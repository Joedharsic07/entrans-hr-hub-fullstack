import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from '@core/guards/auth.guard';
import { LoginComponent } from './pages/login/login.component';
import { SignupComponent } from './pages/signup/signup.component';
import { ResetPasswordComponent } from './pages/reset-password/reset-password.component';
import { ConfrimResetPasswordComponent } from './pages/confrim-reset-password/confrim-reset-password.component';

const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'signup', component: SignupComponent },
  { path: 'password_reset', component: ResetPasswordComponent },
  { path: 'reset-password', component: ConfrimResetPasswordComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AuthenticationRoutingModule { }
