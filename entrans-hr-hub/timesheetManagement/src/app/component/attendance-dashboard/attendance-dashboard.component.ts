import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-attendance-dashboard',
  templateUrl: './attendance-dashboard.component.html',
  styleUrls: ['./attendance-dashboard.component.css']
})
export class AttendanceDashboardComponent implements OnInit {
  attendanceLogs: any[] = [];
  todayLog: any = null;
  currentTime: Date = new Date();
  timer: any;

  constructor(private http: HttpClient, private toastr: ToastrService) {}

  ngOnInit(): void {
    this.fetchAttendance();
    this.timer = setInterval(() => {
      this.currentTime = new Date();
    }, 1000);
  }

  ngOnDestroy(): void {
    if (this.timer) clearInterval(this.timer);
  }

  currentMonth: Date = new Date();
  calendarDays: any[] = [];
  weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  fetchAttendance() {
    this.http.get('http://127.0.0.1:8000/api/attendance/').subscribe({
      next: (data: any) => {
        this.attendanceLogs = data;
        const today = new Date().toISOString().split('T')[0];
        this.todayLog = this.attendanceLogs.find(log => log.date === today) || null;
        this.generateCalendar();
      },
      error: () => this.toastr.error('Failed to load attendance logs')
    });
  }

  previousMonth() {
    this.currentMonth = new Date(this.currentMonth.getFullYear(), this.currentMonth.getMonth() - 1, 1);
    this.generateCalendar();
  }

  nextMonth() {
    this.currentMonth = new Date(this.currentMonth.getFullYear(), this.currentMonth.getMonth() + 1, 1);
    this.generateCalendar();
  }

  generateCalendar() {
    const year = this.currentMonth.getFullYear();
    const month = this.currentMonth.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    this.calendarDays = [];
    
    // Previous month padding
    for (let i = 0; i < firstDay; i++) {
      this.calendarDays.push(null);
    }
    
    // Current month days
    const today = new Date();
    today.setHours(0,0,0,0);
    
    const realToday = new Date();

    for (let i = 1; i <= daysInMonth; i++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
      const log = this.attendanceLogs.find(l => l.date === dateStr);
      const currentDate = new Date(year, month, i);
      const isWeekend = currentDate.getDay() === 0 || currentDate.getDay() === 6;
      const isFuture = currentDate > today;
      const isToday = (currentDate.getFullYear() === realToday.getFullYear() && 
                       currentDate.getMonth() === realToday.getMonth() && 
                       currentDate.getDate() === realToday.getDate());

      let status = '';
      let statusClass = 'bg-gray-50 border-gray-100'; // Default / Future
      
      if (!isFuture) {
        if (log) {
          if (log.attendance_status === 'Present') {
            status = 'P';
            statusClass = 'bg-emerald-50 border-emerald-200';
          } else if (log.attendance_status === 'Half Day') {
            status = 'H';
            statusClass = 'bg-amber-50 border-amber-200';
          } else {
            status = 'A';
            statusClass = 'bg-[#fee2e2] border-[#fca5a5]';
          }
        } else {
          // If no log and it's a weekend, mark as W
          if (isWeekend) {
            status = 'W';
            statusClass = 'bg-[#dbeafe] border-[#bfdbfe]';
          } else {
            status = 'A';
            statusClass = 'bg-[#fee2e2] border-[#fca5a5]';
          }
        }
      }
      
      this.calendarDays.push({
        date: i,
        fullDate: dateStr,
        status: status,
        statusClass: statusClass,
        isFuture: isFuture,
        isWeekend: isWeekend,
        isToday: isToday,
        totalHours: log ? log.total_working_hours : 0,
        log: log
      });
    }
  }

  selectedDay: any = null;

  toggleTooltip(day: any) {
    if (!day || day.isFuture) return;
    if (this.selectedDay === day) {
      this.selectedDay = null;
    } else {
      this.selectedDay = day;
    }
  }

  isPunching: boolean = false;

  punchIn() {
    if (this.isPunching) return;
    this.isPunching = true;
    
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const payload = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          this.http.post('http://127.0.0.1:8000/api/attendance/clock-in/', payload).subscribe({
            next: () => {
              this.toastr.success('Punched in successfully');
              this.fetchAttendance();
              this.isPunching = false;
            },
            error: (err) => {
              this.toastr.error(err.error?.error || 'Failed to punch in');
              this.isPunching = false;
            }
          });
        },
        (error) => {
          this.toastr.error('Location access denied or unavailable. Cannot punch in.');
          this.isPunching = false;
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
    } else {
      this.toastr.error('Geolocation is not supported by your browser.');
      this.isPunching = false;
    }
  }

  punchOut() {
    if (this.isPunching) return;
    this.isPunching = true;

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const payload = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          this.http.post('http://127.0.0.1:8000/api/attendance/clock-out/', payload).subscribe({
            next: () => {
              this.toastr.success('Punched out successfully');
              this.fetchAttendance();
              this.isPunching = false;
            },
            error: (err) => {
              this.toastr.error(err.error?.error || 'Failed to punch out');
              this.isPunching = false;
            }
          });
        },
        (error) => {
          this.toastr.error('Location access denied or unavailable. Cannot punch out.');
          this.isPunching = false;
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
    } else {
      this.toastr.error('Geolocation is not supported by your browser.');
      this.isPunching = false;
    }
  }

  breakStart() {
    this.http.post('http://127.0.0.1:8000/api/attendance/break-start/', {}).subscribe({
      next: () => {
        this.toastr.info('Break started');
        this.fetchAttendance();
      },
      error: (err) => this.toastr.error(err.error?.error || 'Failed to start break')
    });
  }

  breakEnd() {
    this.http.post('http://127.0.0.1:8000/api/attendance/break-end/', {}).subscribe({
      next: () => {
        this.toastr.info('Break ended');
        this.fetchAttendance();
      },
      error: (err) => this.toastr.error(err.error?.error || 'Failed to end break')
    });
  }
}
