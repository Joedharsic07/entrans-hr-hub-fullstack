import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-user-profile',
  templateUrl: './user-profile.component.html',
  styleUrl: './user-profile.component.css'
})
export class UserProfileComponent implements OnInit {
  profile: any;
  userColor: string = '#1F3A5F'; 

ngOnInit(): void {
  this.profile = sessionStorage.getItem('profile');
  this.profile = JSON.parse(this.profile);
  console.log(this.profile);
}
}
