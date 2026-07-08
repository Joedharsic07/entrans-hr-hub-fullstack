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
  timesheetsSubmitted: number = 0;
  activeProjects: number = 0;

  // Recent Activity
  recentActivities: any[] = [];
  activitiesLoading: boolean = true;

  // Upcoming Anniversaries
  upcomingAnniversaries: any[] = [];
  anniversariesLoading: boolean = true;

  ngOnInit(): void {
    if (this.role === 'Admin') {
      this.isAdmin = true;
      this.loadDashboardStats();
      this.loadRecentActivity();
      this.loadUpcomingAnniversaries();
    } else {
      this.loadUserProjects();
    }
  }

  timeAgo(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + ' years ago';
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + ' months ago';
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + ' days ago';
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + ' hours ago';
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + ' minutes ago';
    return Math.floor(seconds) + ' seconds ago';
  }

  loadRecentActivity(): void {
    this.activitiesLoading = true;
    this.service.getAdminRecentActivity().subscribe({
      next: (activities: any[]) => {
        this.recentActivities = activities.map(a => ({
          ...a,
          time: this.timeAgo(a.time)
        }));
        this.activitiesLoading = false;
      },
      error: () => {
        this.activitiesLoading = false;
      }
    });
  }

  loadUpcomingAnniversaries(): void {
    this.anniversariesLoading = true;
    this.service.getAdminUpcomingAnniversaries().subscribe({
      next: (anniversaries: any[]) => {
        this.upcomingAnniversaries = anniversaries;
        this.anniversariesLoading = false;
      },
      error: () => {
        this.anniversariesLoading = false;
      }
    });
  }

  loadDashboardStats(): void {
    this.statsLoading = true;
    
    // Load employee count
    this.service.getAdminUsers({ page_size: 1 }).subscribe({
      next: (res: any) => {
        if (res.count) {
          this.totalEmployees = res.count;
        } else {
          this.totalEmployees = res.length || 0; // fallback if count isn't there
        }
        
        // Load other stats
        this.service.getAdminDashboardStats().subscribe({
          next: (statsRes: any) => {
            this.timesheetsSubmitted = statsRes.timesheets_submitted || 0;
            this.activeProjects = statsRes.active_projects || 0;
            this.statsLoading = false;
          },
          error: () => {
            this.statsLoading = false;
          }
        });
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
