import { Component, OnInit } from '@angular/core';
import { LoginService } from '@core/services/api/login.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HotToastService } from '@ngneat/hot-toast';

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

  // Data Export state
  isExporting = false;

  // Security Settings State
  is2FaEnabled = false;
  show2FaModal = false;
  twoFaCode = '';
  twoFaError = '';
  sessionTimeout = '30m';

  // Edit Profile
  showEditProfile = false;
  editForm!: FormGroup;
  isSaving = false;

  constructor(private loginService: LoginService, private fb: FormBuilder, private toast: HotToastService) {}

  ngOnInit(): void {
    this.editForm = this.fb.group({
      first_name: ['', Validators.required],
      last_name: [''],
      designation: ['']
    });
    const stored = sessionStorage.getItem('profile') || localStorage.getItem('profile');
    if (stored) {
      this.profile = JSON.parse(stored);
    }

    this.loginService.getMyProfile().subscribe({
      next: (data) => {
        this.profile = data;
        this.projects = data.projects || [];
        this.isLoading = false;

        // Load preferences
        const pref2Fa = localStorage.getItem('hrhub_2fa_enabled');
        if (pref2Fa) this.is2FaEnabled = pref2Fa === 'true';

        const prefTimeout = localStorage.getItem('hrhub_session_timeout');
        if (prefTimeout) this.sessionTimeout = prefTimeout;
      },
      error: (err) => {
        console.error('Profile load failed:', err);
        this.isLoading = false;
        this.loadError = true;
        this.projects = [];
      }
    });
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
        this.toast.success('Profile updated successfully');
      },
      error: (err: any) => {
        this.isSaving = false;
        this.toast.error('Failed to update profile');
      }
    });
  }

  exportMyData(): void {
    this.isExporting = true;
    
    // We will compile data from the current component state.
    // If access logs aren't loaded yet, load them first.
    if (this.accessLogs.length === 0) {
      this.loginService.getAccessLogs().subscribe({
        next: (logs) => {
          this.accessLogs = logs;
          this.triggerDownload();
        },
        error: (err) => {
          this.toast.error('Failed to fetch access logs for export.');
          this.triggerDownload(); // Export whatever we have
        }
      });
    } else {
      this.triggerDownload();
    }
  }

  private triggerDownload(): void {
    const exportData = {
      profile: this.profile,
      projects: this.projects,
      recentAccessLogs: this.accessLogs,
      exportedAt: new Date().toISOString()
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `my-hr-hub-data-${new Date().getTime()}.json`;
    link.click();

    URL.revokeObjectURL(url);
    this.isExporting = false;
    this.toast.success('Your data has been successfully exported.');
  }

  // --- Security Settings Methods ---

  toggle2Fa(): void {
    if (this.is2FaEnabled) {
      // Turn off directly
      this.is2FaEnabled = false;
      localStorage.setItem('hrhub_2fa_enabled', 'false');
      this.toast.success('Two-Factor Authentication disabled.');
    } else {
      // Open setup modal
      this.twoFaCode = '';
      this.twoFaError = '';
      this.show2FaModal = true;
    }
  }

  close2FaModal(): void {
    this.show2FaModal = false;
  }

  verify2FaSetup(): void {
    if (!this.twoFaCode || this.twoFaCode.length < 6) {
      this.twoFaError = 'Please enter a valid 6-digit code.';
      return;
    }
    // Simulate verification
    setTimeout(() => {
      this.is2FaEnabled = true;
      localStorage.setItem('hrhub_2fa_enabled', 'true');
      this.show2FaModal = false;
      this.toast.success('Two-Factor Authentication enabled successfully!');
    }, 800);
  }

  onTimeoutChange(event: any): void {
    const val = event.target.value;
    this.sessionTimeout = val;
    localStorage.setItem('hrhub_session_timeout', val);
    this.toast.success('Session timeout preference saved.');
  }
}
