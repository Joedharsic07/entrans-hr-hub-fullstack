import { Component, HostListener } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { LoginService } from '@core/services/api/login.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'timesheetManagement';
  userName: string | null = null;
  userRole: string | null = null;

  // Mobile sidebar
  showMobileSidebar = false;

  // Settings dropdown
  showSettingsDropdown = false;

  // Change password modal
  showChangePwdModal = false;
  cpForm = { old_password: '', new_password: '', confirm_password: '' };
  cpLoading = false;
  cpError = '';
  cpSuccess = '';
  showOldPwd = false;
  showNewPwd = false;
  showConfirmPwd = false;

  constructor(private router: Router, private loginService: LoginService) {
    this.updateUserData(true); // Fetch from API initially
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      this.updateUserData(false);
      this.showSettingsDropdown = false;
      this.showMobileSidebar = false;
    });
  }

  @HostListener('document:click')
  onDocumentClick() {
    this.showSettingsDropdown = false;
  }

  updateUserData(fetchFromApi: boolean = false) {
    if (fetchFromApi) {
      const token = sessionStorage.getItem('accessToken') || localStorage.getItem('accessToken');
      if (token && this.shouldShowNavbar()) {
        this.loginService.getMyProfile().subscribe({
          next: (res) => {
            this.userName = res.name;
            this.userRole = res.role;
            const storage = localStorage.getItem('accessToken') ? localStorage : sessionStorage;
            storage.setItem('name', res.name);
            storage.setItem('role', res.role);
          },
          error: () => {
            this.userName = sessionStorage.getItem('name') || localStorage.getItem('name');
            this.userRole = sessionStorage.getItem('role') || localStorage.getItem('role');
          }
        });
        return;
      }
    }

    // Default fallback to session/local storage for rapid route changes
    this.userName = sessionStorage.getItem('name') || localStorage.getItem('name');
    this.userRole = sessionStorage.getItem('role') || localStorage.getItem('role');
  }

  logout() {
    sessionStorage.clear();
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('profile');
    localStorage.removeItem('name');
    localStorage.removeItem('role');
    this.userName = null;
    this.userRole = null;
    this.router.navigate(['/login']);
  }

  toggleSettings() {
    this.showSettingsDropdown = !this.showSettingsDropdown;
  }

  toggleMobileSidebar() {
    this.showMobileSidebar = !this.showMobileSidebar;
  }

  openChangePassword() {
    this.showSettingsDropdown = false;
    this.cpForm = { old_password: '', new_password: '', confirm_password: '' };
    this.cpError = '';
    this.cpSuccess = '';
    this.showOldPwd = false;
    this.showNewPwd = false;
    this.showConfirmPwd = false;
    this.showChangePwdModal = true;
  }

  closeChangePassword() {
    this.showChangePwdModal = false;
  }

  submitChangePassword() {
    this.cpError = '';
    this.cpSuccess = '';

    if (!this.cpForm.old_password || !this.cpForm.new_password || !this.cpForm.confirm_password) {
      this.cpError = 'All fields are required.';
      return;
    }
    if (this.cpForm.new_password.length < 8) {
      this.cpError = 'New password must be at least 8 characters.';
      return;
    }
    if (this.cpForm.new_password !== this.cpForm.confirm_password) {
      this.cpError = 'New passwords do not match.';
      return;
    }

    this.cpLoading = true;
    this.loginService.changePassword({
      old_password: this.cpForm.old_password,
      new_password: this.cpForm.new_password
    }).subscribe({
      next: (res: any) => {
        this.cpLoading = false;
        this.cpSuccess = res.message || 'Password changed successfully.';
        this.cpForm = { old_password: '', new_password: '', confirm_password: '' };
        setTimeout(() => this.closeChangePassword(), 1500);
      },
      error: (err: any) => {
        this.cpLoading = false;
        this.cpError = err.error?.error || 'Failed to change password.';
      }
    });
  }

  shouldShowNavbar(): boolean {
    const hiddenRoutes = ['/login', '/signup', '/password_reset', '/reset-password'];
    return !hiddenRoutes.some(route => this.router.url.startsWith(route));
  }
}