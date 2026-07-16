import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { LoginService } from '../service/login.service';
import { HotToastService } from '@ngneat/hot-toast';

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrl: './signup.component.css'
})
export class SignupComponent implements OnInit {
  constructor(private fb: FormBuilder, private service: LoginService, private router: Router, private http: HttpClient, private toast: HotToastService) { }
  signupForm!: FormGroup;
  isPasswordVisible: boolean = false;
  isconfirm_passwordVisible: boolean = false;
  isPwdEmpty: boolean = true; // variable for check whether the password field is empty
  passwordPattern: RegExp = /^(?=.*[!@#$%^&(),.*?":{}|<>])(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
  passwordsMatch: boolean = true;
  isLoading: boolean = false;

  ngOnInit(): void {
    this.signupForm = this.fb.group({
      name: [''],
      date_of_joining: [''],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.pattern(this.passwordPattern), Validators.maxLength(12), Validators.minLength(8)],],
      confirm_password: ['', [Validators.required, Validators.pattern(this.passwordPattern), Validators.maxLength(12), Validators.minLength(8)],]
    });
  }

  // submit() {
  //   this.passwordsMatch =
  //     this.signupForm.get("password")?.value ===
  //     this.signupForm.get("confirm_password")?.value;
  //   if (this.passwordsMatch) {
  //     if (this.signupForm.valid) {
  //       const { name, email, password, confirm_password } = this.signupForm.value;
  //       this.service.signup({ name, email, password, confirm_password }).subscribe({
  //         next: (res) => {
  //           alert('Registered Successfully');
  //           this.router.navigate(['/login']);
  //         },
  //         error: (err) => {
  //           if (err.status === 400) {
  //             alert('Email already registered');
  //             this.router.navigate(['/login']);
  //           } else {
  //             alert('Registration failed');
  //           }
  //         }
  //       });
  //     } else {
  //     }
  //   }

  // }

submit() {
  // Start loading
  this.isLoading = true;
  
  this.passwordsMatch = 
    this.signupForm.get("password")?.value ===
    this.signupForm.get("confirm_password")?.value;

  if (!this.passwordsMatch) {
    this.isLoading = false;
    return;
  }

  if (!this.signupForm.valid) {
    this.isLoading = false;
    return;
  }

 
  const { name, email, password, confirm_password, date_of_joining } = this.signupForm.value;
  this.service.signup({ name, email, password, confirm_password, date_of_joining }).subscribe({
    next: (res) => {
      this.isLoading = false; 
      this.toast.success('Registered Successfully');
      this.router.navigate(['/login']);
    },
    error: (err) => {
      this.isLoading = false; 
      if (err.status === 400) {
        this.toast.error('Email already registered');
        this.router.navigate(['/login']);
      } else {
        this.toast.error('Registration failed');
      }
    },
    complete: () => {
      this.isLoading = false;
    }
  });
}

}