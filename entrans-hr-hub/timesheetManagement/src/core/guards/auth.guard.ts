import { ActivatedRouteSnapshot, CanActivate, CanActivateFn, Router, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '@core/authentication/auth.service';
import { Injectable } from '@angular/core';
@Injectable({
  providedIn: 'root'  // Make sure this is present
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(
    next: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): boolean {
    
    const requiredRoles = next.data['roles'] as Array<string>;
    const userRole = this.authService.getUserRole();
    
    // If route doesn't require any specific role but needs authentication
    if (!requiredRoles && !this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return false;
    }
    
    // If specific roles are required
    if (requiredRoles) {
      if (!this.authService.isLoggedIn()) {
        this.router.navigate(['/login']);
        return false;
      }
      
      // Check if user has any of the required roles
      if (requiredRoles.includes(userRole!)) {
        return true;
      }
      
      // If user doesn't have required role
      this.router.navigate(['/login']);
      return false;
    }
    
    // If no specific roles required but user needs to be logged in
    return true;
  }
}


