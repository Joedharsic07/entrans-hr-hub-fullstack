import { HttpClient } from '@angular/common/http';
import { Component, OnInit, NgZone } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { LoginService } from '@core/services/api/login.service';
import { environment } from '@environments/environment';
import { HotToastService } from '@ngneat/hot-toast';

declare const google: any;

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent implements OnInit {
  loginObj ={
    username : '',
    password : ''
  }
  loginForm!: FormGroup;
  isPasswordVisible: boolean = false;
  isLoading: boolean = false;
  isGoogleLoading: boolean = false;
  rememberMe: boolean = false;

  isPwdEmpty: boolean = true; // variable for check whether the password field is empty
  passwordPattern: RegExp = /^(?=.*[!@#$%^&(),.*?":{}|<>])(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/;

  constructor(private fb: FormBuilder, private router: Router, private service:LoginService, private http:HttpClient, private ngZone: NgZone, private toast: HotToastService) { }

  ngOnInit() {
    const accessToken = sessionStorage.getItem('accessToken') || localStorage.getItem('accessToken');
    if (accessToken) {
      const role = sessionStorage.getItem('role') || localStorage.getItem('role');
      if (role === 'Admin') {
        this.router.navigate(['/admin']);
      } else {
        this.router.navigate(['/user-profile']);
      }
      return;
    }

    const savedEmail = localStorage.getItem('rememberedEmail');
    this.rememberMe = !!savedEmail;
    this.loginForm = this.fb.group({
      email: [savedEmail || '', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.pattern(this.passwordPattern), Validators.maxLength(12), Validators.minLength(8)],]
    });
    this.initGoogleSignIn();
  }

  initGoogleSignIn() {
    const checkGoogle = setInterval(() => {
      if (typeof google !== 'undefined' && google.accounts) {
        clearInterval(checkGoogle);
        google.accounts.id.initialize({
          client_id: environment.googleClientId,
          callback: (response: any) => this.handleGoogleCredential(response),
        });
        google.accounts.id.renderButton(
          document.getElementById('google-signin-btn'),
          { theme: 'outline', size: 'large', width: '100%', text: 'signin_with' }
        );
      }
    }, 100);
  }

  handleGoogleCredential(response: any) {
    this.ngZone.run(() => {
      this.isGoogleLoading = true;
      this.service.googleLogin(response.credential).subscribe({
        next: (res: any) => {
          this.isGoogleLoading = false;
          sessionStorage.setItem('accessToken', res.access_token);
          sessionStorage.setItem('refreshToken', res.refresh_token);
          sessionStorage.setItem('profile', JSON.stringify(res.user));
          sessionStorage.setItem('name', res.user.name);
          sessionStorage.setItem('role', res.user.role);
          if (res.user.role === 'Admin') {
            this.router.navigate(['/admin']);
          } else {
            this.router.navigate(['/user-profile']);
          }
        },
        error: (err) => {
          this.isGoogleLoading = false;
          console.error('Google login error:', err);
          if (err.status === 404) {
            this.toast.error('No account found for this Google email. Please contact your administrator.');
          } else if (err.status === 403) {
            this.toast.error('Your account is inactive. Please contact your administrator.');
          } else if (err.status === 0) {
            this.toast.error(`Cannot reach the server. Make sure the backend is running on ${environment.apiUrl}`);
          } else {
            const msg = err.error?.message || err.error?.detail || JSON.stringify(err.error);
            this.toast.error(`Google sign-in failed (${err.status}): ${msg}`);
          }
        }
      });
    });
  }

  onLogin() {
  if (this.loginForm.valid) {
    this.isLoading = true;
    this.service.login(this.loginForm.value).subscribe({
      next: (res: any) => {
        const storage = this.rememberMe ? localStorage : sessionStorage;
        if (this.rememberMe) {
          localStorage.setItem('rememberedEmail', this.loginForm.value.email);
        } else {
          localStorage.removeItem('rememberedEmail');
        }
        storage.setItem('accessToken', res.access_token);
        storage.setItem('refreshToken', res.refresh_token);
        storage.setItem('profile', JSON.stringify(res.user));
        storage.setItem('name', res.user.name);
        storage.setItem('role', res.user.role);
        if (res.user.role === 'Admin') {
          this.router.navigate(['/admin']);
        } else {
          this.router.navigate(['/user-profile']);
        }
      },
      error: (err) => {
        this.isLoading = false;

        if (err.status === 401 || err.status === 400) {
          // Backend rejected credentials
          this.toast.error("Invalid credentials");
        } else {
          // Other unexpected errors
          this.toast.error("Something went wrong. Please try again.");
        }
      }
    });
  }
}


  onSignup(){
    this.router.navigate(['/signup']);
  }
    togglePasswordVisibility(): void {
    this.isPasswordVisible = !this.isPasswordVisible;
  }
}
