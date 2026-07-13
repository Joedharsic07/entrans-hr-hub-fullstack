import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map } from 'rxjs';
import { Observable } from 'rxjs/internal/Observable';
import { environment } from '../../../environment/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
 private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getAccessToken() {
    return sessionStorage.getItem('accessToken') || localStorage.getItem('accessToken');
  }

  getRefreshToken() {
    return sessionStorage.getItem('refreshToken') || localStorage.getItem('refreshToken');
  }

  setAccessToken(token: string) {
    if (localStorage.getItem('accessToken')) {
      localStorage.setItem('accessToken', token);
    } else {
      sessionStorage.setItem('accessToken', token);
    }
  }

  refreshToken(): Observable<string> {
    const refresh_token = this.getRefreshToken();
    
    return this.http.post<{ access_token: string }>(`${this.baseUrl}/refresh-token/`, { refresh_token }).pipe(
      map(res => res.access_token)
    );
  }

  logout() {
    sessionStorage.removeItem('accessToken');
    sessionStorage.removeItem('refreshToken');
    sessionStorage.removeItem('profile');
    sessionStorage.removeItem('name');
    sessionStorage.removeItem('role');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('profile');
    localStorage.removeItem('name');
    localStorage.removeItem('role');
  }
}
