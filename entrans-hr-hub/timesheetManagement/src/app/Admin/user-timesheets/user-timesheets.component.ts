import { Component, OnInit } from '@angular/core';
import { ServiceService } from '../Service/service.service';
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

role=sessionStorage.getItem('role')
  entries: any
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