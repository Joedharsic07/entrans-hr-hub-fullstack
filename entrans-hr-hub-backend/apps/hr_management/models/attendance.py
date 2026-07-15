import datetime
from django.db import models
from .user import User

class AttendanceLog(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendance_logs")
    date = models.DateField(default=datetime.date.today)
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    punch_in_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    punch_in_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    punch_in_address = models.CharField(max_length=255, null=True, blank=True)
    punch_out_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    punch_out_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    punch_out_address = models.CharField(max_length=255, null=True, blank=True)
    is_late_login = models.BooleanField(default=False)
    is_early_logout = models.BooleanField(default=False)
    total_working_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    STATUS_CHOICES = [
        ("Present", "Present"),
        ("Half Day", "Half Day"),
        ("Absent", "Absent"),
    ]
    attendance_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Absent")
    
    def __str__(self):
        return f"{self.employee.name} - {self.date}"

    class Meta:
        app_label = "hr_management"
        db_table = "attendance_log"
        unique_together = ("employee", "date")
        ordering = ["-date"]
