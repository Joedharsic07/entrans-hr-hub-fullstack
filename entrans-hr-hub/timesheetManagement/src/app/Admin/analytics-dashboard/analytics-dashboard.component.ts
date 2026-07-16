import { Component, OnInit, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HotToastService } from '@ngneat/hot-toast';
import {
  ChartComponent,
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexDataLabels,
  ApexTooltip,
  ApexStroke,
  ApexNonAxisChartSeries,
  ApexResponsive
} from "ng-apexcharts";

export type ChartOptions = {
  series: ApexAxisChartSeries | ApexNonAxisChartSeries;
  chart: ApexChart;
  xaxis?: ApexXAxis;
  stroke?: ApexStroke;
  tooltip?: ApexTooltip;
  dataLabels?: ApexDataLabels;
  labels?: any;
  responsive?: ApexResponsive[];
  colors?: string[];
};

@Component({
  selector: 'app-analytics-dashboard',
  templateUrl: './analytics-dashboard.component.html',
  styleUrls: ['./analytics-dashboard.component.css']
})
export class AnalyticsDashboardComponent implements OnInit {
  public attendanceChartOptions: Partial<ChartOptions> | any;
  public leaveChartOptions: Partial<ChartOptions> | any;
  public projectChartOptions: Partial<ChartOptions> | any;
  
  stats: any = {
    active_employees: 0,
    missing_timesheets: 0
  };

  constructor(private http: HttpClient, private toastr: HotToastService) {
    this.initializeEmptyCharts();
  }

  ngOnInit(): void {
    this.fetchAnalytics();
  }

  initializeEmptyCharts() {
    this.attendanceChartOptions = {
      series: [{ name: "Present", data: [] }],
      chart: { height: 350, type: "area", toolbar: { show: false } },
      dataLabels: { enabled: false },
      stroke: { curve: "smooth" },
      xaxis: { categories: [] },
      colors: ['#4f46e5'] // indigo-600
    };

    this.leaveChartOptions = {
      series: [],
      chart: { type: "donut", height: 350 },
      labels: [],
      responsive: [{ breakpoint: 480, options: { chart: { width: 200 }, legend: { position: "bottom" } } }],
      colors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    };

    this.projectChartOptions = {
      series: [{ name: "Members", data: [] }],
      chart: { type: "bar", height: 350, toolbar: { show: false } },
      xaxis: { categories: [] },
      colors: ['#06b6d4']
    };
  }

  fetchAnalytics() {
    this.http.get('http://127.0.0.1:8000/api/analytics/dashboard/').subscribe({
      next: (data: any) => {
        this.stats.active_employees = data.active_employees;
        this.stats.missing_timesheets = data.missing_timesheets;

        // Attendance
        if (data.attendance_trend) {
          this.attendanceChartOptions.series = [{
            name: "Present",
            data: data.attendance_trend.map((x: any) => x.present)
          }];
          this.attendanceChartOptions.xaxis = {
            categories: data.attendance_trend.map((x: any) => x.date)
          };
        }

        // Leave
        if (data.leave_summary) {
          this.leaveChartOptions.series = data.leave_summary.map((x: any) => x.count);
          this.leaveChartOptions.labels = data.leave_summary.map((x: any) => x.leave_type);
        }

        // Projects
        if (data.project_distribution) {
          this.projectChartOptions.series = [{
            name: "Members",
            data: data.project_distribution.map((x: any) => x.member_count)
          }];
          this.projectChartOptions.xaxis = {
            categories: data.project_distribution.map((x: any) => x.name)
          };
        }
      },
      error: () => this.toastr.error('Failed to load analytics data')
    });
  }
}
