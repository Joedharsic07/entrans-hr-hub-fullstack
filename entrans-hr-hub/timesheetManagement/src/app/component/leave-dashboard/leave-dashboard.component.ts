import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HotToastService } from '@ngneat/hot-toast';
import { ServiceService } from '../../shared/Authguard/service.service';
import { environment } from '../../../environment/environment';

@Component({
  selector: 'app-leave-dashboard',
  templateUrl: './leave-dashboard.component.html',
  styleUrls: ['./leave-dashboard.component.css']
})
export class LeaveDashboardComponent implements OnInit {
  leaveBalances: any[] = [];
  leaveHistory: any[] = [];
  isApplyModalOpen = false;
  isAdmin = false;

  newLeave = {
    leave_type: 'CASUAL',
    start_date: '',
    end_date: '',
    reason: ''
  };

  constructor(
    private http: HttpClient, 
    private toastr: HotToastService,
    private authService: ServiceService
  ) {
    this.isAdmin = this.authService.isAdmin();
  }

  ngOnInit(): void {
    if (!this.isAdmin) {
      this.fetchBalances();
    }
    this.fetchHistory();
  }

  fetchBalances() {
    this.http.get(`${environment.apiUrl}/leaves/balances/`).subscribe({
      next: (data: any) => this.leaveBalances = data,
      error: () => this.toastr.error('Failed to load leave balances')
    });
  }

  fetchHistory() {
    this.http.get(`${environment.apiUrl}/leaves/`).subscribe({
      next: (data: any) => this.leaveHistory = data,
      error: () => this.toastr.error('Failed to load leave history')
    });
  }

  openApplyModal() {
    this.isApplyModalOpen = true;
  }

  closeApplyModal() {
    this.isApplyModalOpen = false;
  }

  applyLeave() {
    this.http.post(`${environment.apiUrl}/leaves/`, this.newLeave).subscribe({
      next: () => {
        this.toastr.success('Leave applied successfully');
        this.closeApplyModal();
        this.fetchHistory();
        if (!this.isAdmin) this.fetchBalances();
      },
      error: () => this.toastr.error('Failed to apply leave')
    });
  }

  updateLeaveStatus(leaveId: number, status: string) {
    this.http.patch(`${environment.apiUrl}/leaves/${leaveId}/`, { status }).subscribe({
      next: () => {
        this.toastr.success(`Leave ${status} successfully`);
        this.fetchHistory();
      },
      error: (err: any) => {
        this.toastr.error(err.error?.error || `Failed to ${status} leave`);
      }
    });
  }
}
