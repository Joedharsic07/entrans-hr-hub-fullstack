import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { LoginService } from '@core/services/api/login.service';

@Component({
  selector: 'app-create-user',
  templateUrl: './create-user.component.html',
  styleUrl: './create-user.component.css'
})
export class CreateUserComponent {
  createUserForm: FormGroup;
  isLoading = false;
  successMessage = '';
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private loginService: LoginService
  ) {
    this.createUserForm = this.fb.group({
      first_name: ['', [Validators.required, Validators.minLength(2)]],
      last_name: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      designation: [''],
      date_of_joining: [''],
      role: ['user', Validators.required]
    });
  }

  onSubmit(): void {
    if (this.createUserForm.invalid) return;

    this.isLoading = true;
    this.successMessage = '';
    this.errorMessage = '';

    this.loginService.createUser(this.createUserForm.value).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.successMessage = res.message || 'User created successfully.';
        this.createUserForm.reset({ role: 'user' });
      },
      error: (err: any) => {
        this.isLoading = false;
        this.errorMessage = err.error?.error || 'Failed to create user. Please try again.';
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/admin']);
  }
}
