import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../../environment/environment';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ServiceService {

  constructor(private httpClient:HttpClient) { }
  baseUrl:string = environment.apiUrl;
  timesheetValidation(File:any): Observable<any>{
    return this.httpClient.post(`${this.baseUrl}/time-tracking/validation/`,File)
  }
  sendValidationEmail(emailData: any) {
    return this.httpClient.post(`${this.baseUrl}/time-tracking/send-email/`, emailData);
  }
  generatePpt(formData: FormData) {
    return this.httpClient.post(`${this.baseUrl}/ppt-automation/`, formData, {
      responseType: 'blob'
    });
}
  userTimesheetlist(){
    return this.httpClient.get(`${this.baseUrl}/user-timesheets/`)
  }
  createProject(projectData: any): Observable<any> {
    return this.httpClient.post(`${this.baseUrl}/projects/`, projectData);
  }
  getUsers(): Observable<any> {
    return this.httpClient.get(`${this.baseUrl}/users/`);
  }
  getUserProjects(month: string, year: string): Observable<any> {
  return this.httpClient.get(`${this.baseUrl}/validate-multiple-timesheets/`, {
    params: {
      month,
      year
    }
  });
}
  validationTimesheet(validationData: any): Observable<any> {
    return this.httpClient.post(`${this.baseUrl}/validate-multiple-timesheets/`, validationData);
  }
  pushEmail(data: any) {
  return this.httpClient.post(`${this.baseUrl}/push-email/`, data);
}

}
