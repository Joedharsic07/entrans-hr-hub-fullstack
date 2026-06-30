import { Component } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'timesheetManagement';
  userName: string | null = null;
  userRole: string | null = null;
  showHeader: boolean = true;

  constructor(private router: Router) {
    // Initialize user data
    this.updateUserData();

    // Update user data on route changes
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      this.updateUserData();
    });
  }

  // Method to update user data from sessionStorage
  updateUserData() {
    this.userName = sessionStorage.getItem('name');
    this.userRole = sessionStorage.getItem('role');
  }

  logout() {
    sessionStorage.clear();
    this.userName = null;
    this.userRole = null;
    this.router.navigate(['/login']);
  }

  openProfile() {
    this.router.navigate(['/user-profile']);
  }

  shouldShowNavbar(): boolean {
    const hiddenRoutes = ['/login', '/signup', '/password_reset', '/reset-password'];
    return !hiddenRoutes.some(route => this.router.url.startsWith(route));
  }
}