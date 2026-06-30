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
resetLink(data: any): Observable<any> {
  return this.http.post(`${this.baseUrl}/request-password-reset/`, data)
}
resetPassword(data: any): Observable<any> {
  return this.http.post(`${this.baseUrl}/confirm-password-reset/`, data)
}
}
