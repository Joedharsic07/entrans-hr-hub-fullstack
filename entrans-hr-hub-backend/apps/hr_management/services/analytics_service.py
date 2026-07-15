import datetime
from django.db.models import Count
from hr_management.models.attendance import AttendanceLog
from hr_management.models.leave import LeaveRequest
from hr_management.models.project import Project
from hr_management.models.user import User

class AnalyticsService:
    @staticmethod
    def get_dashboard_data():
        today = datetime.date.today()
        first_day_of_month = today.replace(day=1)
        
        attendance_trend = []
        for i in range(6, -1, -1):
            d = today - datetime.timedelta(days=i)
            count = AttendanceLog.objects.filter(date=d).count()
            attendance_trend.append({"date": d.strftime("%Y-%m-%d"), "present": count})

        leave_summary = LeaveRequest.objects.filter(
            start_date__gte=first_day_of_month,
            status='approved'
        ).values('leave_type').annotate(count=Count('id'))

        project_distribution = Project.objects.annotate(
            member_count=Count('userproject')
        ).values('name', 'member_count')

        active_employees = User.objects.filter(is_active=True).count()
        missing_timesheets = 12 

        return {
            "attendance_trend": attendance_trend,
            "leave_summary": list(leave_summary),
            "project_distribution": list(project_distribution),
            "active_employees": active_employees,
            "missing_timesheets": missing_timesheets
        }
