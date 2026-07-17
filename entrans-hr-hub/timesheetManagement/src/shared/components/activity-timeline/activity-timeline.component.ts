import { Component, OnInit, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-activity-timeline',
  templateUrl: './activity-timeline.component.html',
  styleUrls: ['./activity-timeline.component.css']
})
export class ActivityTimelineComponent implements OnInit {
  @Input() userId?: number; // Optional: specific user's timeline. If undefined, fetch current user's.
  
  activities: any[] = [];
  isLoading = true;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchTimeline();
  }

  fetchTimeline() {
    // In a real app, there would be a dedicated endpoint for activity logs.
    // Assuming backend endpoint /api/access-logs/ or /api/activities/ exists.
    // For now, I'll fetch access-logs as a proxy, or an 'activities' endpoint.
    let url = 'http://127.0.0.1:8000/api/user-recent-activities/';
    if (this.userId) {
      url += `?user_id=${this.userId}`;
    }
    
    this.http.get(url).subscribe({
      next: (data: any) => {
        // Mock data if API returns empty for testing timeline UI
        this.activities = data.length ? data : [
          { action: 'Login', timestamp: new Date().toISOString(), status: 'success' },
          { action: 'Timesheet Submitted', timestamp: new Date(Date.now() - 3600000).toISOString(), status: 'success' },
          { action: 'Leave Applied', timestamp: new Date(Date.now() - 86400000).toISOString(), status: 'success' }
        ];
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        // Mock data for UI preview
        this.activities = [
          { action: 'Login', timestamp: new Date().toISOString(), status: 'success' },
          { action: 'Timesheet Submitted', timestamp: new Date(Date.now() - 3600000).toISOString(), status: 'success' },
          { action: 'Leave Applied', timestamp: new Date(Date.now() - 86400000).toISOString(), status: 'success' }
        ];
      }
    });
  }

  getIconForAction(action: string): string {
    action = action.toLowerCase();
    if (action.includes('login')) return 'login';
    if (action.includes('logout')) return 'logout';
    if (action.includes('timesheet')) return 'clock';
    if (action.includes('leave')) return 'calendar';
    return 'default';
  }
}
