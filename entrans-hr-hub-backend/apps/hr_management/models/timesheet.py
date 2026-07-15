from django.db import models
from .user import User
from .project import UserProject

class Timesheet(models.Model):
    WORKTYPE_CHOICES = [
        ("working", "Working"),
        ("weekend", "Weekend"),
        ("holiday", "Holiday"),
        ("half_day_leave", "Half Day Leave"),
        ("full_day_leave", "Full Day Leave"),
    ]
    user_project = models.ForeignKey(UserProject, on_delete=models.CASCADE)
    date = models.DateField()
    task_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True)
    duration = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )
    work_type = models.CharField(
        max_length=20, choices=WORKTYPE_CHOICES, default="working"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Timesheet - {self.user_project.user.name} ({self.date})"

    class Meta:
        app_label = "hr_management"
        db_table = "timesheet"


class HolidayWeekend(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description

    class Meta:
        app_label = "hr_management"
        db_table = "holiday_weekend"


class TimesheetEmailLog(models.Model):
    recipient = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="email_logs",
    )
    project_name = models.CharField(max_length=255)
    status = models.TextField()
    email_content = models.JSONField()
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sent_emails",
    )

    def __str__(self):
        return f"Email to {self.recipient} for {self.project_name} - {self.status}"

    class Meta:
        app_label = "hr_management"
        db_table = "timesheet_email_log"
