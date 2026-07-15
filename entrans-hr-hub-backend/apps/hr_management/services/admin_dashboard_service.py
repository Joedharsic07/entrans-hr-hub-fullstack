from django.db.models.functions import ExtractMonth, ExtractYear
from datetime import date
from hr_management.models.timesheet import Timesheet, TimesheetEmailLog
from hr_management.models.project import Project
from hr_management.models.user import User, UserAccessLog
from hr_management.models import PPTGenerationLog

class AdminDashboardService:
    @staticmethod
    def get_stats():
        total_timesheets = Timesheet.objects.annotate(
            year=ExtractYear('date'),
            month=ExtractMonth('date')
        ).values('user_project__user', 'year', 'month').distinct().count()
        
        active_projects = Project.objects.count()
        return {
            "timesheets_submitted": total_timesheets,
            "active_projects": active_projects
        }

    @staticmethod
    def get_recent_activities():
        activities = []
        
        access_logs = UserAccessLog.objects.select_related("user").order_by("-timestamp")[:5]
        for log in access_logs:
            icon = "bi bi-check-circle-fill" if log.status == "success" else "bi bi-exclamation-triangle-fill"
            iconClass = "activity-icon--green" if log.status == "success" else "activity-icon--amber"
            action_text = "logged in" if log.action == "login" else log.action.replace("_", " ")
            text = f"<strong>{log.user.name}</strong> {action_text} ({log.status})"
            activities.append({
                "icon": icon,
                "iconClass": iconClass,
                "text": text,
                "time": log.timestamp.isoformat(),
                "type": "System Access",
                "timestamp_obj": log.timestamp
            })
            
        email_logs = TimesheetEmailLog.objects.select_related("recipient").order_by("-sent_at")[:5]
        for log in email_logs:
            icon = "bi bi-envelope-check-fill" if log.status == "success" else "bi bi-envelope-exclamation-fill"
            iconClass = "activity-icon--purple" if log.status == "success" else "activity-icon--amber"
            recipient_name = log.recipient.name if log.recipient else "Unknown"
            text = f"Automated timesheet email sent to <strong>{recipient_name}</strong> for {log.project_name}"
            activities.append({
                "icon": icon,
                "iconClass": iconClass,
                "text": text,
                "time": log.sent_at.isoformat(),
                "type": "Automated Email",
                "timestamp_obj": log.sent_at
            })
            
        ppt_logs = PPTGenerationLog.objects.select_related("created_by").order_by("-created_at")[:5]
        for log in ppt_logs:
            creator_name = log.created_by.name if log.created_by else "System"
            text = f"<strong>{creator_name}</strong> generated Anniversary Slides for {log.employee_name}"
            activities.append({
                "icon": "bi bi-easel2-fill",
                "iconClass": "activity-icon--blue",
                "text": text,
                "time": log.created_at.isoformat(),
                "type": "PPT Generation",
                "timestamp_obj": log.created_at
            })
            
        activities.sort(key=lambda x: x["timestamp_obj"], reverse=True)
        top_activities = activities[:5]
        
        for act in top_activities:
            del act["timestamp_obj"]
            
        return top_activities

    @staticmethod
    def get_upcoming_anniversaries():
        today = date.today()
        users = User.objects.filter(date_of_joining__month=today.month, is_active=True)
        
        anniversaries = []
        for user in users:
            years = today.year - user.date_of_joining.year
            if years > 0:
                anniversaries.append({
                    "name": f"{user.first_name} {user.last_name}".strip() or user.name,
                    "years": f"{years} Years",
                    "date": user.date_of_joining.strftime("%b %d"),
                    "day_of_month": user.date_of_joining.day
                })
                
        anniversaries.sort(key=lambda x: x["day_of_month"])
        return anniversaries
