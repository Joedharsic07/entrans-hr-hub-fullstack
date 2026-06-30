import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environment/environment';

@Injectable({
  providedIn: 'root'
})
export class TimesheetService {

constructor(private http: HttpClient) {}

 private baseUrl = environment.apiUrl;

  getProjectById(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/users/${id}/projects/`);
  }
  
  getTimeSheet(id:any,user_project_id:any,month:any, year:any):Observable<any>{
    return this.http.get(`${this.baseUrl}/timesheets/?project_id=${id}&user_project=${user_project_id}&month_year=${month}/${year}`)
  }
  
  updateTimesheet(id:number,data:any):Observable<any>{
    return this.http.patch(`${this.baseUrl}/timesheets/${id}/`,data)
  }

  addTimesheet(data:any):Observable<any>{
    return this.http.post(`${this.baseUrl}/timesheets/`,data)
  }
}
