import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HotToastService } from '@ngneat/hot-toast';
import { TimesheetService } from '../../timesheet/service/timesheet.service';

@Component({
  selector: 'app-user-timesheets-list',
  templateUrl: './user-timesheets-list.component.html',
  styleUrl: './user-timesheets-list.component.css'
})
export class UserTimesheetsListComponent {
years: number[] = [];
  months: string[] = [];
  selectedYear!: number;
  selectedMonth!: number;
  userName: any
  userRole: any
  dates: string[] = [];
  dayDetails: {
    label?: string;
    dateFormatted: string;
    dayName: string;
    isWeekend: boolean;
    absent: string;
    user_project: string;
    id: any;
    task_name: string;
    description: string;
    duration: number;
    work_type: string;
    day_type?: string
  }[] = [];
  
  statistics: any

  absentOptions = ['working', 'weekend', 'holiday', 'half_day_leave', 'full_day_leave'];
  selectedAbsentRow: number | null = null;
  projectName: any
  showPopup = false;
  popupDescription = '';
  popupRowIndex: any;
  descriptions: any;
  paramId: any
  projectsData: any
  selectedProjectId: any
  selectedUserProjectId:any
  userProjectId: any
  timeSheetData: any
  isSidebarVisible: boolean = true;

  savingRowIds: Set<string> = new Set();
  savedRowIds: Set<string> = new Set();

  get isReadOnly(): boolean {
    return this.userRole === 'Admin';
  }

  constructor(private service: TimesheetService, private activatedRoute: ActivatedRoute,private toastr: HotToastService,private router:Router) { }
  ngOnInit(): void {
    const currentYear = new Date().getFullYear();
    const futureYear = currentYear + 10;

    this.years = Array.from({ length: futureYear - currentYear + 1 }, (_, i) => currentYear + i);
    this.months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    this.userName = sessionStorage.getItem('name') || localStorage.getItem('name');
    this.userRole = sessionStorage.getItem('role') || localStorage.getItem('role');

    console.log(this.userName, this.userRole)
    this.selectedYear = currentYear;
    this.selectedMonth = new Date().getMonth(); // 0-based (Jan = 0)

    this.activatedRoute?.params.subscribe(paramData => {
      this.paramId = paramData;
      if (Object.keys(paramData).length) {
        // this.service.getProjectById(this.paramId?.id).subscribe((data) => {
        //   this.projectsData = data;
          this.selectedProjectId =  this.paramId?.projectId;
          this.selectedUserProjectId=this.paramId?.userProjectId
          // this.projectName = this.projectsData[0].name

          // Now generate days and fetch timesheet

          this.getTimeSheet(this.selectedProjectId, this.selectedUserProjectId, this.selectedMonth + 1, this.selectedYear); // +1 for API
        // });
      }
    });
    this.generateDaysForMonth(this.selectedYear, this.selectedMonth);

  }

  onMonthOrYearChange() {
    this.generateDaysForMonth(this.selectedYear, this.selectedMonth);
    this.descriptions = [];
    this.selectedAbsentRow = null;

  }

  generateDaysForMonth(year: number, month: number) {
    this.dates = [];
    this.dayDetails = [];

    const date = new Date(year, month, 1);
    while (date.getMonth() == month) {
      const dayName = date.toLocaleDateString('en-GB', { weekday: 'long' }); // Tuesday
      const dateFormatted = date.toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });
      const isWeekend = date.getDay() === 0 || date.getDay() === 6;
      this.dayDetails.push({
        label: '',
        dateFormatted,
        dayName,
        isWeekend,
        absent: isWeekend ? 'weekend' : 'working',
        user_project: this.userProjectId,
        id: '',
        task_name: '',
        description: '',
        duration: 0,
        work_type: ''
      });

      date.setDate(date.getDate() + 1);
    }
  }

  onAbsentSelect(index: number, value: string) {
    this.dayDetails[index].absent = value;
  }

  getRowClass(day: any) {
    if (day.absent === 'weekend') {
      return 'weekend-row';
    }
    return '';
  }

  goToPreviousMonth() {
    if (this.selectedMonth === 0) {
      this.selectedMonth = 11;
      this.selectedYear--;
    } else {
      this.selectedMonth--;
    }
    this.getTimeSheet(this.selectedProjectId, this.selectedUserProjectId, this.selectedMonth + 1, this.selectedYear)

    this.onMonthOrYearChange();
  }

  goToNextMonth() {
    if (this.selectedMonth === 11) {
      this.selectedMonth = 0;
      this.selectedYear++;
    } else {
      this.selectedMonth++;
    }
    this.getTimeSheet(this.selectedProjectId,this.selectedUserProjectId, this.selectedMonth + 1, this.selectedYear)
    this.onMonthOrYearChange();
  }

  // timeSheet(projectId: any, userProjectId: any, projectName: string) {
  //   this.selectedProjectId = projectId
  //   this.userProjectId = userProjectId
  //   this.projectName = projectName
  //   this.getTimeSheet(this.selectedProjectId, this.selectedMonth + 1, this.selectedYear)
  // }
  formatDateToISO(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toISOString().split('T')[0]; // 'YYYY-MM-DD'
  }

  formatDate(date: any): string {
    const d = new Date(date);
    return d.toLocaleDateString('en-CA'); // Outputs 'YYYY-MM-DD'
  }

  getTimeSheet(selectedProjectId: number, selectedUserProjectId:number,selectedMonth: number, selectedYear: number) {
  this.service.getTimeSheet(selectedProjectId,selectedUserProjectId, selectedMonth, selectedYear).subscribe((data) => {
    this.timeSheetData = data.timesheets || [];
    this.statistics = data.statistics;
    this.projectName=this.timeSheetData[0].project_name
    this.dayDetails.forEach((day) => {
      const isoDate = this.convertFormattedDateToISO(day.dateFormatted);
      const matchingEntry = this.timeSheetData.find((entry: any) => entry.date === isoDate);

      if (matchingEntry) {
        // Update all fields from the matching entry
        day.id = matchingEntry.id;
        day.task_name = matchingEntry.task_name;
        day.description = matchingEntry.description;
        day.duration = matchingEntry.duration;
        day.work_type = matchingEntry.work_type;
        day.absent = matchingEntry.work_type; // Keep absent in sync
      } else {
        // Reset fields but maintain the date info
        day.id = '';
        day.task_name = '';
        day.description = '';
        day.duration = 0;
        day.work_type = day.isWeekend ? 'weekend' : 'working';
        day.absent = day.work_type;
      }
    });
  });
}

  convertFormattedDateToISO(formattedDate: string): string {
    const [day, monthStr, year] = formattedDate.split(' ');
    const months: any = {
      January: '01', February: '02', March: '03', April: '04',
      May: '05', June: '06', July: '07', August: '08',
      September: '09', October: '10', November: '11', December: '12'
    };
    const month = months[monthStr];
    return `${year}-${month}-${day.padStart(2, '0')}`;
  }

logout() {
  sessionStorage.clear();
  this.router.navigate(['/login']);
}
toggleSidebar() {
  this.isSidebarVisible = !this.isSidebarVisible;
}
openProfile() {
  this.router.navigate(['/user-profile']);
}
navigate(){
  this.router.navigate(['/admin'])
}
navigateToTimesheet(){
  this.router.navigate(['/admin'])
}
capitalizeFirstLetter(text: string): string {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1).replace(/_/g, ' ');
}
getDescriptionRowCount(description: string): number {
  if (!description) return 1;
  const wordCount = description.trim().split(/\s+/).length;
  return wordCount > 20 ? 2 : 1;
}

saveRow(day: any): void {
  const isoDate = this.convertFormattedDateToISO(day.dateFormatted);
  const payload = {
    user_project: this.selectedUserProjectId,
    date: isoDate,
    task_name: day.task_name || '',
    description: day.description || '',
    duration: day.duration || 0,
    work_type: day.work_type || 'working'
  };

  this.savingRowIds.add(day.dateFormatted);

  const onSuccess = (res: any) => {
    if (!day.id && res?.id) day.id = res.id;
    this.savingRowIds.delete(day.dateFormatted);
    this.savedRowIds.add(day.dateFormatted);
    setTimeout(() => this.savedRowIds.delete(day.dateFormatted), 2000);
    this.toastr.success('Row saved successfully');
  };
  const onError = () => {
    this.savingRowIds.delete(day.dateFormatted);
    this.toastr.error('Failed to save row');
  };

  if (day.id) {
    this.service.updateTimesheet(day.id, payload).subscribe({ next: onSuccess, error: onError });
  } else {
    this.service.addTimesheet(payload).subscribe({ next: onSuccess, error: onError });
  }
}

autoSave(day: any): void {
  if (this.isReadOnly) return;
  if (this.isDateFuture(day.dateFormatted)) return;
  this.saveRow(day);
}

isDateFuture(dateFormatted: string): boolean {
  const isoDate = this.convertFormattedDateToISO(dateFormatted);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const rowDate = new Date(isoDate);
  rowDate.setHours(0, 0, 0, 0);
  return rowDate > today;
}

}

