import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HotToastService } from '@ngneat/hot-toast';

@Component({
  selector: 'app-attendance-dashboard',
  templateUrl: './attendance-dashboard.component.html',
  styleUrls: ['./attendance-dashboard.component.css']
})
export class AttendanceDashboardComponent implements OnInit {
  attendanceLogs: any[] = [];
  paginatedLogs: any[] = [];
  currentPage: number = 1;
  totalPages: number = 1;
  pageSize: number = 3;
  totalCount: number = 0;
  todayLog: any = null;
  currentTime: Date = new Date();
  timer: any;
  isLoadingCalendar: boolean = true;
  isLoadingLogs: boolean = true;

  constructor(private http: HttpClient, private toastr: HotToastService) {}

  ngOnInit(): void {
    this.timer = setInterval(() => {
      this.currentTime = new Date();
      this.updateLiveHours();
    }, 1000);
    this.fetchAttendance();
    this.fetchPaginatedAttendance(this.currentPage);
  }

  updateLiveHours() {
    if (this.todayLog && this.todayLog.clock_in && !this.todayLog.clock_out) {
      const now = new Date();
      const clockIn = new Date(this.todayLog.clock_in);
      const diffMs = now.getTime() - clockIn.getTime();
      const hrs = Math.floor(diffMs / 3600000);
      const mins = Math.floor((diffMs % 3600000) / 60000);
      this.liveTotalHours = `${hrs}h ${mins}m`;
    } else if (this.todayLog && this.todayLog.clock_out) {
      const clockIn = new Date(this.todayLog.clock_in);
      const clockOut = new Date(this.todayLog.clock_out);
      const diffMs = clockOut.getTime() - clockIn.getTime();
      const hrs = Math.floor(diffMs / 3600000);
      const mins = Math.floor((diffMs % 3600000) / 60000);
      this.liveTotalHours = `${hrs}h ${mins}m`;
    } else {
      this.liveTotalHours = '0h 0m';
    }
  }

  get todayStatus(): string {
    if (!this.todayLog?.clock_in) {
      return 'Not Started';
    }
    if (this.todayLog?.clock_in && !this.todayLog?.clock_out) {
      return 'Working';
    }
    return this.todayLog.attendance_status || 'Absent';
  }

  get todayStatusClasses(): any {
    const status = this.todayStatus;
    if (status === 'Present') {
      return {
        card: 'bg-emerald-50 border-emerald-100',
        text: 'text-emerald-700',
        dot: 'bg-emerald-500'
      };
    }
    if (status === 'Half Day') {
      return {
        card: 'bg-amber-50 border-amber-100',
        text: 'text-amber-700',
        dot: 'bg-amber-500'
      };
    }
    if (status === 'Absent' || status === 'Not Started') {
      return {
        card: 'bg-red-50 border-red-100',
        text: 'text-red-700',
        dot: 'bg-red-500'
      };
    }
    // Working
    return {
      card: 'bg-blue-50 border-blue-100',
      text: 'text-blue-700',
      dot: 'bg-blue-500'
    };
  }

  padZero(num: number): string {
    return num < 10 ? '0' + num : num.toString();
  }

  ngOnDestroy(): void {
    if (this.timer) clearInterval(this.timer);
  }

  currentMonth: Date = new Date();
  calendarDays: any[] = [];
  weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  leaveBalances: any[] = [];
  sickLeaveBalance: any = null;
  earnedLeaveBalance: any = null;
  leaves: any[] = [];
  liveTotalHours: string = '0h 0m';

  fetchAttendance() {
    this.isLoadingCalendar = true;
    this.http.get('http://127.0.0.1:8000/api/attendance/').subscribe({
      next: (data: any) => {
        this.attendanceLogs = data;
        const realToday = new Date();
        const year = realToday.getFullYear();
        const month = String(realToday.getMonth() + 1).padStart(2, '0');
        const day = String(realToday.getDate()).padStart(2, '0');
        const todayStr = `${year}-${month}-${day}`;
        this.todayLog = this.attendanceLogs.find((log: any) => log.date === todayStr) || null;
        this.updateLiveHours();
        this.generateCalendar();
        this.isLoadingCalendar = false;
      },
      error: () => {
        this.toastr.error('Failed to load attendance logs');
        this.isLoadingCalendar = false;
      }
    });
    
    this.fetchLeaveBalances();
    this.fetchLeaves();
  }

  fetchLeaves() {
    this.http.get('http://127.0.0.1:8000/api/leaves/').subscribe({
      next: (data: any) => {
        this.leaves = data.filter((l: any) => l.status === 'approved');
        this.generateCalendar();
      },
      error: () => console.error('Failed to load leaves')
    });
  }

  fetchPaginatedAttendance(page: number) {
    this.isLoadingLogs = true;
    this.http.get(`http://127.0.0.1:8000/api/attendance/?page=${page}&page_size=${this.pageSize}`).subscribe({
      next: (data: any) => {
        this.paginatedLogs = data.results;
        this.currentPage = page;
        this.totalCount = data.count;
        this.totalPages = Math.ceil(data.count / this.pageSize);
        this.isLoadingLogs = false;
      },
      error: () => {
        this.toastr.error('Failed to load paginated logs');
        this.isLoadingLogs = false;
      }
    });
  }

  goToPage(page: number) {
    if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
      this.fetchPaginatedAttendance(page);
    }
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

  fetchLeaveBalances() {
    this.http.get('http://127.0.0.1:8000/api/leaves/balances/').subscribe({
      next: (data: any) => {
        this.leaveBalances = data;
        this.sickLeaveBalance = this.leaveBalances.find(b => b.leave_type === 'SICK') || null;
        this.earnedLeaveBalance = this.leaveBalances.find(b => b.leave_type === 'EARNED') || null;
      },
      error: () => console.error('Failed to load leave balances')
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
      
      const leave = this.leaves.find(l => {
        const start = new Date(l.start_date);
        start.setHours(0,0,0,0);
        const end = new Date(l.end_date);
        end.setHours(0,0,0,0);
        const curr = new Date(currentDate);
        curr.setHours(0,0,0,0);
        return curr >= start && curr <= end;
      });
      
      if (leave && !isWeekend) {
        if (leave.leave_type === 'SICK' || leave.leave_type === 'Sick Leave' || leave.leave_type === 'Sick') {
          status = 'SL';
          statusClass = 'bg-cyan-50 border-cyan-200';
        } else if (leave.leave_type === 'EARNED' || leave.leave_type === 'Earned Leave' || leave.leave_type === 'Earned') {
          status = 'EL';
          statusClass = 'bg-purple-50 border-purple-200';
        } else {
          status = 'L';
          statusClass = 'bg-orange-50 border-orange-200';
        }
      } else if (!isFuture) {
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

    // Next month padding
    const remainingDays = this.calendarDays.length % 7;
    if (remainingDays !== 0) {
      const paddingDays = 7 - remainingDays;
      for (let i = 0; i < paddingDays; i++) {
        this.calendarDays.push(null);
      }
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
    
    // Bypass geolocation for local testing to prevent browser prompt hangs
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      this.executePunchIn({ latitude: 12.9716, longitude: 77.5946 });
      return;
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const payload = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          this.executePunchIn(payload);
        },
        (error) => {
          this.toastr.warning('Location access denied. Using fallback location for testing.');
          this.executePunchIn({ latitude: 12.9716, longitude: 77.5946 });
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
      );
    } else {
      this.toastr.warning('Geolocation not supported. Using fallback location.');
      this.executePunchIn({ latitude: 12.9716, longitude: 77.5946 });
    }
  }

  private executePunchIn(payload: any) {
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
  }

  punchOut() {
    if (this.isPunching) return;
    this.isPunching = true;

    // Bypass geolocation for local testing to prevent browser prompt hangs
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      this.executePunchOut({ latitude: 12.9716, longitude: 77.5946 });
      return;
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const payload = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          this.executePunchOut(payload);
        },
        (error) => {
          this.toastr.warning('Location access denied. Using fallback location for testing.');
          this.executePunchOut({ latitude: 12.9716, longitude: 77.5946 });
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
      );
    } else {
      this.toastr.warning('Geolocation not supported. Using fallback location.');
      this.executePunchOut({ latitude: 12.9716, longitude: 77.5946 });
    }
  }

  private executePunchOut(payload: any) {
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
