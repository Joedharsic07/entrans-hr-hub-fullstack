import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { LoginService } from '@core/services/api/login.service';

@Component({
  selector: 'app-reset-password',
  templateUrl: './reset-password.component.html',
  styleUrl: './reset-password.component.css'
})
export class ResetPasswordComponent implements OnInit{
   submitted = false;
   forgotPasswordForm !: FormGroup;
  message = '';
  error = '';
  loading= false;
  constructor(private fb: FormBuilder, private http: HttpClient, private service: LoginService) {}
ngOnInit() {
  this.forgotPasswordForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]]
  });
}
  
  onSubmit() {
    this.submitted = true;
    if (this.forgotPasswordForm.invalid) return;
    this.loading = true;
    this.service.resetLink(this.forgotPasswordForm.value).subscribe({
      next: () => {
        this.message = 'Reset link has been sent to your email.';
        this.error = '';
        this.loading = false;
      },
      error: err => {
        this.error = err.error?.message || 'Something went wrong.';
        this.message = '';
        this.loading = false;
      }
    });
  }

}
