import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environment/environment';

@Injectable({
  providedIn: 'root'
})
export class LoginService {

   private baseUrl = environment.apiUrl;
   private header = new HttpHeaders({
    'Content-Type': 'application/json'
  });


  constructor(private http: HttpClient) {}

signup(data: any): Observable<any> {
  return this.http.post(`${this.baseUrl}/register/`, data)
}
login(data: any): Observable<any> {
  return this.http.post(`${this.baseUrl}/login/`, data)
}
googleLogin(credential: string): Observable<any> {
  return this.http.post(`${this.baseUrl}/google-login/`, { credential })
}
resetLink(data: any): Observable<any> {
  return this.http.post(`${this.baseUrl}/request-password-reset/`, data)
}
resetPassword(data: any): Observable<any> {
  return this.http.post(`${this.baseUrl}/confirm-password-reset/`, data)
}
createUser(data: any): Observable<any> {
  return this.http.post(`${this.baseUrl}/create-user/`, data)
}
changePassword(data: any): Observable<any> {
  return this.http.post(`${this.baseUrl}/change-password/`, data)
}
getMyProfile(): Observable<any> {
  return this.http.get(`${this.baseUrl}/me/`)
}
updateProfile(data: any): Observable<any> {
  return this.http.put(`${this.baseUrl}/me/`, data)
}
getAccessLogs(): Observable<any> {
  return this.http.get(`${this.baseUrl}/access-logs/`)
}
}
