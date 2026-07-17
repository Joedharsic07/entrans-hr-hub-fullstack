import { Component, OnInit } from '@angular/core';
import { ServiceService } from '@core/services/api/admin.service';
import { Route, Router } from '@angular/router';
// interface TimesheetEntry {
//   userName: string;
//   projectName: string;
//   timesheetLink: string;
// }

@Component({
  selector: 'app-user-timesheets',
  templateUrl: './user-timesheets.component.html',
  styleUrl: './user-timesheets.component.css'
})
export class UserTimesheetsComponent implements OnInit {
isAdmin :boolean =false

role = sessionStorage.getItem('role') || localStorage.getItem('role')
  entries: any
  currentPage: number = 1;
  pageSize: number = 10;

  get totalPages(): number {
    return Math.max(1, Math.ceil((this.entries?.length || 0) / this.pageSize));
  }

  get paginatedEntries(): any[] {
    if (!this.entries) return [];
    const start = (this.currentPage - 1) * this.pageSize;
    return this.entries.slice(start, start + this.pageSize);
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

  goToPage(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
    }
  }

  constructor(private serive: ServiceService, private router:Router) { }
  ngOnInit(): void {
    this.serive.userTimesheetlist().subscribe((res) => {
      this.entries = res
      console.log(this.entries);
      if(this.role==="Admin") this.isAdmin=true
     if(this.isAdmin) {
      this.entries = this.entries.flatMap((user: any) =>
        user.projects.map((project: any) => ({
          user_name: user.user_name,
          user_email:user.user_email,
          projectName: project.project_name,
          timesheetLink: project.timesheets_link
        }))
      );   
    }
      if(!this.isAdmin) {
        this.entries =  this.entries.projects.map((project: any) => ({
          user_name:  this.entries.user_name,
          user_email:  this.entries.user_email,
          projectName: project.project_name,
          timesheetLink: `/timesheet/${this.entries.user_id}`
        }));
        console.log(this.entries);
        
      }
    })
  }
  navigate(timesheetLink: any){
     this.router.navigate([timesheetLink]);
  }
}