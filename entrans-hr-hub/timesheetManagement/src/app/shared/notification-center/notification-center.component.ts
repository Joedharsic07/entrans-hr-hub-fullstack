import { Component, OnInit, HostListener, ElementRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HotToastService } from '@ngneat/hot-toast';

@Component({
  selector: 'app-notification-center',
  templateUrl: './notification-center.component.html',
  styleUrls: ['./notification-center.component.css']
})
export class NotificationCenterComponent implements OnInit {
  notifications: any[] = [];
  unreadCount: number = 0;
  isOpen: boolean = false;

  constructor(private http: HttpClient, private toastr: HotToastService, private eRef: ElementRef) {}

  ngOnInit(): void {
    this.fetchNotifications();
    // Poll every minute
    setInterval(() => this.fetchNotifications(), 60000);
  }

  @HostListener('document:click', ['$event'])
  clickout(event: Event) {
    if(!this.eRef.nativeElement.contains(event.target)) {
      this.isOpen = false;
    }
  }

  toggleDropdown() {
    this.isOpen = !this.isOpen;
  }

  fetchNotifications() {
    this.http.get('http://127.0.0.1:8000/api/notifications/').subscribe({
      next: (data: any) => {
        this.notifications = data;
        this.unreadCount = this.notifications.filter(n => !n.is_read).length;
      }
    });
  }

  markAsRead(id: number) {
    this.http.post(`http://127.0.0.1:8000/api/notifications/${id}/read/`, {}).subscribe({
      next: () => this.fetchNotifications()
    });
  }

  markAllAsRead() {
    this.http.post('http://127.0.0.1:8000/api/notifications/read/', {}).subscribe({
      next: () => {
        this.fetchNotifications();
        this.toastr.success('All notifications marked as read');
      }
    });
  }

  deleteNotification(id: number, event: Event) {
    event.stopPropagation();
    this.http.delete(`http://127.0.0.1:8000/api/notifications/${id}/`).subscribe({
      next: () => {
        this.fetchNotifications();
      }
    });
  }
}
