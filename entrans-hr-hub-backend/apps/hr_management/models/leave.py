from django.db import models
from .user import User

class LeaveType(models.TextChoices):
    CASUAL = "CASUAL", "Casual Leave"
    SICK = "SICK", "Sick Leave"
    EARNED = "EARNED", "Earned Leave"
    WFH = "WFH", "Work From Home"
    COMP_OFF = "COMP_OFF", "Comp Off"

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    approver = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_leaves")
    applied_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type} ({self.start_date} to {self.end_date})"

    class Meta:
        app_label = "hr_management"
        db_table = "leave_request"
        ordering = ["-applied_on"]

class LeaveBalance(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_balances")
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    total_days = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)

    @property
    def remaining_days(self):
        return self.total_days - self.used_days

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type} ({self.remaining_days} remaining)"

    class Meta:
        app_label = "hr_management"
        db_table = "leave_balance"
        unique_together = ("employee", "leave_type")
