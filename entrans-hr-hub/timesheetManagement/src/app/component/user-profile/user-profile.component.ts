import { Component, OnInit } from '@angular/core';
import { LoginService } from '../service/login.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-user-profile',
  templateUrl: './user-profile.component.html',
  styleUrl: './user-profile.component.css'
})
export class UserProfileComponent implements OnInit {
  profile: any = null;
  projects: any[] = [];
  isLoading = true;
  loadError = false;

  // Access logs
  accessLogs: any[] = [];
  showAccessLogs = false;
  logsLoading = false;

  // Dynamic password-changed display
  passwordChangedText = '—';

  // Edit Profile
  showEditProfile = false;
  editForm!: FormGroup;
  isSaving = false;

  constructor(private loginService: LoginService, private fb: FormBuilder) {}

  ngOnInit(): void {
    this.editForm = this.fb.group({
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      designation: ['']
    });
    const stored = sessionStorage.getItem('profile');
    if (stored) {
      this.profile = JSON.parse(stored);
    }

    this.loginService.getMyProfile().subscribe({
      next: (data) => {
        this.profile = data;
        this.projects = data.projects || [];
        this.isLoading = false;
        this.computePasswordChangedText();
      },
      error: (err) => {
        console.error('Profile load failed:', err);
        this.isLoading = false;
        this.loadError = true;
        this.projects = [];
      }
    });
  }

  computePasswordChangedText(): void {
    const ts = this.profile?.password_changed_at;
    if (!ts) {
      this.passwordChangedText = 'Never';
      return;
    }
    const days = Math.floor((Date.now() - new Date(ts).getTime()) / 86_400_000);
    if (days === 0) this.passwordChangedText = 'Today';
    else if (days === 1) this.passwordChangedText = '1d ago';
    else this.passwordChangedText = `${days}d ago`;
  }

  openAccessLogs(): void {
    this.showAccessLogs = true;
    if (this.accessLogs.length === 0) {
      this.logsLoading = true;
      this.loginService.getAccessLogs().subscribe({
        next: (logs) => {
          this.accessLogs = logs;
          this.logsLoading = false;
        },
        error: () => { this.logsLoading = false; }
      });
    }
  }

  closeAccessLogs(): void {
    this.showAccessLogs = false;
  }

  formatAction(action: string): string {
    const labels: Record<string, string> = {
      login: 'Login',
      logout: 'Logout',
      password_change: 'Password Changed',
      password_reset: 'Password Reset',
    };
    return labels[action] ?? action;
  }

  getInitial(): string {
    if (!this.profile?.name) return '?';
    return this.profile.name.charAt(0).toUpperCase();
  }

  getOwnerCount(): number {
    return this.projects.filter(p => p.role === 'owner').length;
  }

  getCollaboratorCount(): number {
    return this.projects.filter(p => p.role === 'collaborator').length;
  }

  openEditProfile(): void {
    if (this.profile) {
      this.editForm.patchValue({
        first_name: this.profile.first_name || '',
        last_name: this.profile.last_name || '',
        designation: this.profile.designation || ''
      });
    }
    this.showEditProfile = true;
  }

  closeEditProfile(): void {
    this.showEditProfile = false;
  }

  saveProfile(): void {
    if (this.editForm.invalid) return;
    this.isSaving = true;
    this.loginService.updateProfile(this.editForm.value).subscribe({
      next: (res: any) => {
        this.profile = res.user;
        sessionStorage.setItem('profile', JSON.stringify(res.user));
        this.isSaving = false;
        this.showEditProfile = false;
      },
      error: (err: any) => {
        this.isSaving = false;
        alert('Failed to update profile');
      }
    });
  }
}
