import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { LoginService } from '../service/login.service';

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

  isPwdEmpty: boolean = true; // variable for check whether the password field is empty
  passwordPattern: RegExp = /^(?=.*[!@#$%^&(),.*?":{}|<>])(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/;

  constructor(private fb: FormBuilder, private router: Router, private service:LoginService, private http:HttpClient) { }
ngOnInit() {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.pattern(this.passwordPattern), Validators.maxLength(12), Validators.minLength(8)],]
    })
    }
onLogin() {
  if (this.loginForm.valid) {
    this.isLoading = true;
    this.service.login(this.loginForm.value).subscribe({
      next: (res: any) => {
        // Successful login
        sessionStorage.setItem('accessToken', res.access_token);
        sessionStorage.setItem('refreshToken', res.refresh_token);
        sessionStorage.setItem('profile',JSON.stringify(res.user));
        sessionStorage.setItem('name', res.user.name);
        sessionStorage.setItem('role', res.user.role);
        const role = res.user.role;
         this.router.navigate(['/admin']);
      },
      error: (err) => {
        this.isLoading = false;

        if (err.status === 401 || err.status === 400) {
          // Backend rejected credentials
          alert("Invalid credentials");
        } else {
          // Other unexpected errors
          alert("Something went wrong. Please try again.");
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
