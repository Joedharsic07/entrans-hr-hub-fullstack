import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class ServiceService {

  constructor(private router: Router) {}

  login(credentials: any): Promise<boolean> {
    // Your login logic that sets the role in sessionStorage
    // Example:
    // return this.http.post('/api/login', credentials).toPromise()
    //   .then((res: any) => {
    //     sessionStorage.setItem('role', res.user.role);
    //     return true;
    //   })
    //   .catch(() => false);
    return Promise.resolve(true); // Replace with actual implementation
  }

  logout(): void {
    sessionStorage.removeItem('role');
    sessionStorage.removeItem('accessToken');
    sessionStorage.removeItem('refreshToken');
    sessionStorage.removeItem('profile');
    sessionStorage.removeItem('name');
    localStorage.removeItem('role');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('profile');
    localStorage.removeItem('name');
    this.router.navigate(['/login']);
  }

  getUserRole(): string | null {
    return sessionStorage.getItem('role') || localStorage.getItem('role');
  }

  isLoggedIn(): boolean {
    return this.getUserRole() !== null;
  }

  isAdmin(): boolean {
    return this.getUserRole() === 'Admin';
  }
}
