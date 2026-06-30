import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css'
})
export class SidebarComponent implements OnInit {

  sidebarHidden = false;
  isAdmin :boolean =false
  showTimesheetDropdown = false;

 role=sessionStorage.getItem('role')

  ngOnInit(): void {
     if(this.role==="Admin") this.isAdmin=true
  }
  toggleSidebar() {
    this.sidebarHidden = !this.sidebarHidden;
  }
  toggleTimesheetDropdown() {
  this.showTimesheetDropdown = !this.showTimesheetDropdown;
}
}
  