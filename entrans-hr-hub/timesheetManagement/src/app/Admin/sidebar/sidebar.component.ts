import { Component, OnInit } from '@angular/core';
import { LoginService } from '../../component/service/login.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css'
})
export class SidebarComponent implements OnInit {

  sidebarHidden = false;
  isAdmin: boolean = false;
  showTimesheetDropdown = false;
  showUserDropdown = false;
  showChangePasswordModal = false;

  userName = sessionStorage.getItem('name') || '';
  userRole = sessionStorage.getItem('role') || '';

  // Change Password form state
  cpForm = { old_password: '', new_password: '', confirm_password: '' };
  cpLoading = false;
  cpError = '';
  cpSuccess = '';
  showOldPwd = false;
  showNewPwd = false;
  showConfirmPwd = false;

  constructor(private loginService: LoginService) {}

  ngOnInit(): void {
    if (this.userRole === 'Admin') this.isAdmin = true;
  }

  toggleSidebar(): void {
    this.sidebarHidden = !this.sidebarHidden;
  }

  toggleTimesheetDropdown(): void {
    this.showTimesheetDropdown = !this.showTimesheetDropdown;
  }

  toggleUserDropdown(): void {
    this.showUserDropdown = !this.showUserDropdown;
  }

  openChangePassword(): void {
    this.showUserDropdown = false;
    this.cpForm = { old_password: '', new_password: '', confirm_password: '' };
    this.cpError = '';
    this.cpSuccess = '';
    this.showChangePasswordModal = true;
  }

  closeChangePassword(): void {
    this.showChangePasswordModal = false;
  }

  submitChangePassword(): void {
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
}
