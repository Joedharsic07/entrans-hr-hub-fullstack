import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { LoginService } from '@core/services/api/login.service';

@Component({
  selector: 'app-confrim-reset-password',
  templateUrl: './confrim-reset-password.component.html',
  styleUrl: './confrim-reset-password.component.css'
})
export class ConfrimResetPasswordComponent {
token = '';
  submitted = false;
  message = '';
  error = '';
  resetForm!: FormGroup;
  isNewPasswordVisible = false;
  isConfirmPasswordVisible = false;
    passwordPattern: RegExp = /^(?=.*[!@#$%^&(),.*?":{}|<>])(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/;


  constructor(private route: ActivatedRoute, private fb: FormBuilder, private http: HttpClient,private service: LoginService) {}

  ngOnInit(): void {
    this.token = this.route.snapshot.queryParamMap.get('token') || '';
    this.resetForm = this.fb.group({
    new_password:  ['', [Validators.required, Validators.pattern(this.passwordPattern), Validators.maxLength(12), Validators.minLength(8)],],
    confirm_password:  ['', [Validators.required, Validators.pattern(this.passwordPattern), Validators.maxLength(12), Validators.minLength(8)],]
    });
  }

  onSubmit() {
    this.submitted = true;
    const { new_password, confirm_password } = this.resetForm.value;

    if (this.resetForm.invalid || new_password !== confirm_password) {
      this.error = 'Passwords do not match or are invalid.';
      return;
    }

    this.service.resetPassword({
      token: this.token,
      new_password
    }).subscribe({
      next: () => {
        this.message = 'Password reset successful. You can now log in.';
        this.error = '';
      },
      error: err => {
        this.error = err.error?.message || 'Failed to reset password.';
        this.message = '';
      }
    });
  }
  toggleNewPasswordVisibility() {
    this.isNewPasswordVisible = !this.isNewPasswordVisible;
  }

  toggleConfirmPasswordVisibility() {
    this.isConfirmPasswordVisible = !this.isConfirmPasswordVisible;
  }

}
