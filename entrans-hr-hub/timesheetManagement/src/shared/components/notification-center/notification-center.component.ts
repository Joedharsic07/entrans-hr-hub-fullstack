import { Component, OnInit, OnDestroy, HostListener, ElementRef, NgZone } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '@core/authentication/auth.service';
import { HotToastService } from '@ngneat/hot-toast';
import { environment } from '@environments/environment';

@Component({
  selector: 'app-notification-center',
  templateUrl: './notification-center.component.html',
  styleUrls: ['./notification-center.component.css']
})
export class NotificationCenterComponent implements OnInit, OnDestroy {
  notifications: any[] = [];
  unreadCount: number = 0;
  isOpen: boolean = false;
  private abortController: AbortController | null = null;

  constructor(private http: HttpClient, private toastr: HotToastService, private eRef: ElementRef, private zone: NgZone, private authService: AuthService) {}
  baseUrl: string = environment.apiUrl;

  ngOnInit(): void {
    this.fetchNotifications();
    this.setupSSE();
  }

  ngOnDestroy(): void {
    if (this.abortController) {
      this.abortController.abort();
    }
  }

  async setupSSE() {
    const token = this.authService.getAccessToken();
    if (token) {
      this.abortController = new AbortController();
      try {
        const response = await fetch(`${this.baseUrl}/notifications/stream/`, {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          signal: this.abortController.signal
        });

        const reader = response.body?.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            
            let splitIndex;
            while ((splitIndex = buffer.indexOf('\n\n')) >= 0) {
              const message = buffer.slice(0, splitIndex);
              buffer = buffer.slice(splitIndex + 2);
              
              if (message.startsWith('data: ')) {
                const dataStr = message.substring(6);
                try {
                  const data = JSON.parse(dataStr);
                  this.zone.run(() => {
                    this.notifications = data;
                    this.unreadCount = this.notifications.filter((n: any) => !n.is_read).length;
                  });
                } catch (e) {
                  console.error('Error parsing SSE data:', e);
                }
              }
            }
          }
        }
      } catch (error: any) {
        if (error.name !== 'AbortError') {
          console.error('SSE Error:', error);
        }
      }
    }
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
    this.http.get(`${this.baseUrl}/notifications/`).subscribe({
      next: (data: any) => {
        this.notifications = data;
        this.unreadCount = this.notifications.filter(n => !n.is_read).length;
      }
    });
  }

  markAsRead(id: number) {
    this.http.post(`${this.baseUrl}/notifications/${id}/read/`, {}).subscribe({
      next: () => this.fetchNotifications()
    });
  }

  markAllAsRead() {
    this.http.post(`${this.baseUrl}/notifications/read/`, {}).subscribe({
      next: () => {
        this.fetchNotifications();
        this.toastr.success('All notifications marked as read');
      }
    });
  }

  deleteNotification(id: number, event: Event) {
    event.stopPropagation();
    this.http.delete(`${this.baseUrl}/notifications/${id}/`).subscribe({
      next: () => {
        this.fetchNotifications();
      }
    });
  }
}
