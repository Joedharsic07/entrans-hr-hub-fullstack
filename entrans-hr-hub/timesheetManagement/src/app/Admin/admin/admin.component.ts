import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ServiceService } from '../Service/service.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrl: './admin.component.css'
})
export class AdminComponent implements OnInit {
  constructor(public router: Router, private service: ServiceService) { }

  showTimesheetOptions: boolean = false;
  isAdmin: boolean = false;

  role = sessionStorage.getItem('role');
  userName = sessionStorage.getItem('name') || 'Joe Dharsic';
  userRole = sessionStorage.getItem('role') || 'Administrator';

  // Non-admin user projects
  userProjects: any[] = [];
  projectsLoading = false;

  // Dashboard stats
  statsLoading: boolean = true;
  totalEmployees: number | null = null;
  timesheetsSubmitted: number = 942;
  pendingApprovals: number = 43;

  // Recent Activity
  recentActivities: any[] = [
    {
      icon: 'bi bi-check-circle-fill',
      iconClass: 'activity-icon--green',
      text: '<strong>Sarah Jenkins</strong> approved 14 timesheets for <a class="activity-link">Project Orion</a>',
      time: '2 minutes ago',
      type: 'Automated Sync'
    },
    {
      icon: 'bi bi-person-plus-fill',
      iconClass: 'activity-icon--purple',
      text: 'New user <strong>Marcus Thorne</strong> added to <a class="activity-link">Lead Developer</a> role',
      time: '45 minutes ago',
      type: 'Admin Action'
    },
    {
      icon: 'bi bi-exclamation-triangle-fill',
      iconClass: 'activity-icon--amber',
      text: 'Flagged discrepancy in <strong>Project Zenith</strong> billing cycle',
      time: '2 hours ago',
      type: 'System Alert'
    }
  ];

  // Upcoming Anniversaries
  upcomingAnniversaries: any[] = [
    { name: 'Elena Rodriguez', years: '5 Years', date: 'Oct 14' },
    { name: 'Kenji Tanaka', years: '2 Years', date: 'Oct 16' }
  ];

  ngOnInit() {
    if (this.role === 'Admin') {
      this.isAdmin = true;
      this.loadDashboardStats();
    } else {
      this.loadUserProjects();
    }
  }

  loadDashboardStats(): void {
    this.statsLoading = true;
    // Load real stats from service
    this.service.getAdminUsers({ page_size: 1 }).subscribe({
      next: (res: any) => {
        if (res.count) {
          this.totalEmployees = res.count;
        } else {
          this.totalEmployees = res.length || 0; // fallback if count isn't there
        }
        this.statsLoading = false;
      },
      error: () => {
        this.totalEmployees = 0;
        this.statsLoading = false;
      }
    });
  }

  loadUserProjects(): void {
    this.projectsLoading = true;
    this.service.userTimesheetlist().subscribe({
      next: (res: any) => {
        this.userProjects = res.projects || [];
        this.projectsLoading = false;
      },
      error: () => { this.projectsLoading = false; }
    });
  }

  navigateToTimesheet(timesheetsLink: string): void {
    this.router.navigate(['/' + timesheetsLink]);
  }

  navigateToTimesheetOptions() {
    this.showTimesheetOptions = true;
  }

  navigateToTimesheet_upload() {
    this.showTimesheetOptions = false;
    this.router.navigate(['/timesheet']);
  }

  navigateToValidationTimesheet() {
    this.showTimesheetOptions = false;
    this.router.navigate(['/validation-timesheet']);
  }

  navigateToPpt() {
    this.router.navigate(['/ppt-automation']);
  }

  navigateToCreateProject() {
    this.router.navigate(['/create-project']);
  }

  navigateToProjectMembers() {
    this.router.navigate(['/project-members']);
  }

  logout() {
    sessionStorage.clear();
    this.router.navigate(['/login']);
  }
}
