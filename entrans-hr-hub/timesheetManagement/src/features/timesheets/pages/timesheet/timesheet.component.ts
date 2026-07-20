import { Component, OnInit } from '@angular/core';
import { TimesheetService } from '@features/timesheets/services/timesheet.service';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-timesheet',
  templateUrl: './timesheet.component.html',
  styleUrl: './timesheet.component.css'
})
export class TimesheetComponent implements OnInit {
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
    day_type?: string;
    statusMessage?: string;
    hasStatusWarning?: boolean;
  }[] = [];

  statistics: any

absentOptions = [
  { name: 'Working', value: 'working' },
  { name: 'Weekend', value: 'weekend' },
  { name: 'Holiday', value: 'holiday' },
  { name: 'Half Day Leave', value: 'half_day_leave' },
  { name: 'Full Day Leave', value: 'full_day_leave' }
];
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
  
  constructor(private service: TimesheetService, private activatedRoute: ActivatedRoute,private router:Router) { }
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

    this.selectedYear = currentYear;
    this.selectedMonth = new Date().getMonth(); // 0-based (Jan = 0)

    this.activatedRoute?.params.subscribe(paramData => {
      this.paramId = paramData;
      if (Object.keys(paramData).length) {
        this.service.getProjectById(this.paramId?.id).subscribe((data) => {
          this.projectsData = data;
          this.selectedProjectId = this.projectsData[0].id;
          this.selectedUserProjectId= this.projectsData[0].user_project_id
          this.projectName = this.projectsData[0].name

          // Now generate days and fetch timesheet
          this.getTimeSheet(this.selectedProjectId, this.selectedUserProjectId, this.selectedMonth + 1, this.selectedYear); // +1 for API
        });
      }
    });
    this.getProjects();
    this.generateDaysForMonth(this.selectedYear, this.selectedMonth);

  }
  getProjects() {
    this.service.getProjectById(this.paramId?.id).subscribe((projects) => {
      this.projectsData = projects;
      if (this.projectsData.length > 0) {
        const firstProject = this.projectsData[0];
        this.selectedProjectId = firstProject.id;
        // this.projectName=firstProject.name
        this.timeSheet(firstProject.id, firstProject.user_project_id, firstProject.name);
      }
    });
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

  openDescriptionPopup(index: number) {
    this.popupRowIndex = index;
    this.popupDescription = this.dayDetails[index]?.description || '';
    this.showPopup = true;
  }

  closePopup() {
    this.showPopup = false;
    this.popupRowIndex = null;
    this.popupDescription = '';
  }


  saveDescription() {
    if (this.popupRowIndex != null) {
      const day = this.dayDetails[this.popupRowIndex];
      day.description = this.popupDescription;
      this.updateSingleField(day);
    }
    this.closePopup();
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
    this.getTimeSheet(this.selectedProjectId,this.userProjectId ,this.selectedMonth + 1, this.selectedYear)

    this.onMonthOrYearChange();
  }

  goToNextMonth() {
    if (this.selectedMonth === 11) {
      this.selectedMonth = 0;
      this.selectedYear++;
    } else {
      this.selectedMonth++;
    }
    this.getTimeSheet(this.selectedProjectId,this.userProjectId, this.selectedMonth + 1, this.selectedYear)
    this.onMonthOrYearChange();
  }

  timeSheet(projectId: any, userProjectId: any, projectName: string) {
    this.selectedProjectId = projectId
    this.userProjectId = userProjectId
    this.projectName = projectName
    this.getTimeSheet(projectId,userProjectId, this.selectedMonth + 1, this.selectedYear)
  }
  formatDateToISO(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toISOString().split('T')[0]; // 'YYYY-MM-DD'
  }

  formatDate(date: any): string {
    const d = new Date(date);
    return d.toLocaleDateString('en-CA'); // Outputs 'YYYY-MM-DD'
  }

  getTimeSheet(selectedProjectId: number,selectedUserProjectId:number, selectedMonth: number, selectedYear: number) {
  this.service.getTimeSheet(selectedProjectId, selectedUserProjectId, selectedMonth, selectedYear).subscribe((data) => {
    this.timeSheetData = data.timesheets || [];
    this.statistics = data.statistics;

    this.dayDetails.forEach((day) => {
      const isoDate = this.convertFormattedDateToISO(day.dateFormatted);
      const matchingEntry = this.timeSheetData.find((entry: any) => entry.date === isoDate );
      
      if (matchingEntry) {
        // Update all fields from the matching entry
        day.id = matchingEntry.id;
        day.task_name = matchingEntry.task_name;
        day.description = matchingEntry.description;
        day.duration = matchingEntry.duration;
        day.work_type = matchingEntry.work_type;
        day.absent = matchingEntry.work_type;
        day.statusMessage = matchingEntry.Status || null; 
        day.hasStatusWarning = matchingEntry.Status && matchingEntry.Status !== 'Valid';
      } 
      else {
        // Reset fields but maintain the date info
        day.id = '';
        day.task_name = '';
        day.description = '';
        day.duration = 0;
        day.work_type = day.isWeekend ? 'weekend' : 'working';
        day.absent = day.work_type;
        day.statusMessage = undefined;
        day.hasStatusWarning = false;
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

updateSingleField(day: any) {
  // Use work_type if available, otherwise use absent
  console.log(day);
  
  const workType = day.work_type || day.absent;
  let taskName = day.task_name;
let description = day.description;
let duration = day.duration;

// For non-working types, preserve existing values if any exist in timeSheetData
if (!['working', 'half_day_leave'].includes(workType)) {
 const existing = this.timeSheetData.find((entry: any) =>
  entry.date === this.convertFormattedDateToISO(day.dateFormatted) && !!entry.id
);


  if (existing) {
    taskName = existing.task_name || taskName;
    description = existing.description || description;
    duration = existing.duration ?? duration;
  }
}
  
  const data = {
    task_name: day.task_name, 
    description: day.description,
    duration: day.duration,
    work_type: workType,
    date: this.convertFormattedDateToISO(day.dateFormatted),
    user_project: this.userProjectId
  };

  // Check if we should validate (only for working/half_day_leave)
  const needsValidation = ['working', 'half_day_leave'].includes(workType);
  const isValid = !needsValidation || (
    data.task_name && data.task_name.trim() !== '' &&
    data.duration > 0
  );

  if (!isValid) return;

  // Always check if we have an existing entry for this date
  const existingEntry = this.timeSheetData.find((entry: any) => 
    entry.date === data.date && !!entry.id
  );
  
  if (existingEntry || day.id) {
    // Use day.id if available, otherwise use existingEntry.id
    const idToUpdate = day.id || existingEntry.id;
    
    this.service.updateTimesheet(idToUpdate, data).subscribe({
      next: (res) => {
        this.getTimeSheet(this.selectedProjectId,this.userProjectId, this.selectedMonth + 1, this.selectedYear)

        if (existingEntry) {
          Object.assign(existingEntry, data);
        } else {
          const newEntry = {...data, id: res.id};
          this.timeSheetData.push(newEntry);
        }
        day.id = idToUpdate || res.id;
      },
      
    });
  } else {
    this.service.addTimesheet(data).subscribe({
      next: (res) => {
        // Add to local data
        const newEntry = {...data, id: res.id};
        this.timeSheetData.push(newEntry);
        this.getTimeSheet(this.selectedProjectId,this.userProjectId, this.selectedMonth + 1, this.selectedYear)

        day.id = res.id; 
      },
      
    });
  }
}
  updateData(id: number, data: any) {
    this.service.updateTimesheet(id, data).subscribe({
      next: () => console.log(`Updated timesheet ${id}`),
      error: (err) => console.error(`Error updating timesheet ${id}:`, err)
    });
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
capitalizeFirstLetter(text: string): string {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1).replace(/_/g, ' ');
}
getDescriptionRowCount(description: string): number {
  if (!description) return 1;
  const wordCount = description.trim().split(/\s+/).length;
  return wordCount > 20 ? 2 : 1;
}
}
