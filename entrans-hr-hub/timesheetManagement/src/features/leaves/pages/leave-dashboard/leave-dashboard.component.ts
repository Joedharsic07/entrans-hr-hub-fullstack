import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HotToastService } from '@ngneat/hot-toast';
import { AuthService } from '@core/authentication/auth.service';
import { environment } from '@environments/environment';

@Component({
  selector: 'app-leave-dashboard',
  templateUrl: './leave-dashboard.component.html',
  styleUrls: ['./leave-dashboard.component.css']
})
export class LeaveDashboardComponent implements OnInit {
  leaveBalances: any[] = [
    { leave_type: 'SICK', remaining_days: 0 },
    { leave_type: 'EARNED', remaining_days: 0 }
  ];
  leaveHistory: any[] = [];
  isApplyModalOpen = false;
  isAdmin = false;
  isLoading = false;
  isRefreshing = false;
  isSubmittingLeave = false;
  processingLeaveId: number | null = null;
  processingAction: string | null = null;

  currentPage = 1;
  pageSize = 5;

  get paginatedHistory() {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.leaveHistory.slice(start, start + this.pageSize);
  }

  get totalPages() {
    return Math.max(1, Math.ceil(this.leaveHistory.length / this.pageSize));
  }

  get pageNumbers(): number[] {
    const total = this.totalPages;
    const cur = this.currentPage;
    if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
    const pages: number[] = [];
    for (let i = 1; i <= total; i++) {
      if (i === 1 || i === total || (i >= cur - 2 && i <= cur + 2)) {
        pages.push(i);
      } else if (pages.length > 0 && pages[pages.length - 1] !== -1) {
        pages.push(-1);
      }
    }
    return pages;
  }

  get currentRangeEnd() {
    return Math.min(this.currentPage * this.pageSize, this.leaveHistory.length);
  }

  nextPage() {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
    }
  }

  prevPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }

  goToPage(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
    }
  }

  newLeave = {
    leave_type: 'CASUAL',
    start_date: '',
    end_date: '',
    reason: ''
  };

  constructor(
    private http: HttpClient, 
    private toastr: HotToastService,
    private authService: AuthService
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
      next: (data: any) => {
        const defaultBalances = [
          { leave_type: 'SICK', remaining_days: 0 },
          { leave_type: 'EARNED', remaining_days: 0 }
        ];
        
        this.leaveBalances = defaultBalances.map(defaultBal => {
          const found = data.find((b: any) => b.leave_type === defaultBal.leave_type);
          return found || defaultBal;
        });
      },
      error: () => this.toastr.error('Failed to load leave balances')
    });
  }

  fetchHistory(isRefresh = false) {
    if (isRefresh) {
      this.isRefreshing = true;
    } else {
      this.isLoading = true;
    }

    this.http.get(`${environment.apiUrl}/leaves/`).subscribe({
      next: (data: any) => {
        this.leaveHistory = data;
        this.currentPage = 1; // Reset to first page when new data arrives
        this.isLoading = false;
        this.isRefreshing = false;
      },
      error: () => {
        this.toastr.error('Failed to load leave history');
        this.isLoading = false;
        this.isRefreshing = false;
      }
    });
  }

  refreshData() {
    this.fetchHistory(true);
    if (!this.isAdmin) {
      this.fetchBalances();
    }
  }

  openApplyModal() {
    this.isApplyModalOpen = true;
  }

  closeApplyModal() {
    this.isApplyModalOpen = false;
  }

  applyLeave() {
    this.isSubmittingLeave = true;
    this.http.post(`${environment.apiUrl}/leaves/`, this.newLeave).subscribe({
      next: () => {
        this.toastr.success('Leave applied successfully');
        this.isSubmittingLeave = false;
        this.closeApplyModal();
        this.fetchHistory();
        if (!this.isAdmin) this.fetchBalances();
      },
      error: (err: any) => {
        this.toastr.error(err.error?.error || 'Failed to apply leave');
        this.isSubmittingLeave = false;
      }
    });
  }

  updateLeaveStatus(leaveId: number, status: string) {
    this.processingLeaveId = leaveId;
    this.processingAction = status;
    this.http.patch(`${environment.apiUrl}/leaves/${leaveId}/`, { status }).subscribe({
      next: () => {
        this.toastr.success(`Leave ${status} successfully`);
        this.processingLeaveId = null;
        this.processingAction = null;
        this.fetchHistory();
      },
      error: (err: any) => {
        this.toastr.error(err.error?.error || `Failed to ${status} leave`);
        this.processingLeaveId = null;
        this.processingAction = null;
      }
    });
  }
}
