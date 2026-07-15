from django.db import models
from .user import User

class Notification(models.Model):
    TYPE_CHOICES = [
        ("leave_approved", "Leave Approved"),
        ("leave_rejected", "Leave Rejected"),
        ("project_assigned", "Project Assigned"),
        ("timesheet_reminder", "Timesheet Reminder"),
        ("new_employee", "New Employee Added"),
        ("password_expiry", "Password Expiry"),
        ("work_anniversary", "Work Anniversary"),
        ("birthday", "Birthday"),
        ("system_announcement", "System Announcement"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.notification_type}"

    class Meta:
        app_label = "hr_management"
        db_table = "notification"
        ordering = ["-created_at"]


class ActivityLog(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activity_timeline")
    action_type = models.CharField(max_length=100)  # Login, Logout, Timesheet Submitted, Leave Applied, etc.
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.action_type} - {self.timestamp}"

    class Meta:
        app_label = "hr_management"
        db_table = "activity_log"
        ordering = ["-timestamp"]
