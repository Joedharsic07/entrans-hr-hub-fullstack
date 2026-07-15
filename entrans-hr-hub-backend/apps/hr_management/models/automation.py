from django.db import models

class MonthChoices(models.TextChoices):
    JANUARY = "JAN", "January"
    FEBRUARY = "FEB", "February"
    MARCH = "MAR", "March"
    APRIL = "APR", "April"
    MAY = "MAY", "May"
    JUNE = "JUN", "June"
    JULY = "JUL", "July"
    AUGUST = "AUG", "August"
    SEPTEMBER = "SEP", "September"
    OCTOBER = "OCT", "October"
    NOVEMBER = "NOV", "November"
    DECEMBER = "DEC", "December"


class TimesheetType(models.TextChoices):
    UPLOAD = "UPLOAD", "Upload Validation"
    AUTO = "AUTO", "Automated Validation"
    MANUAL = "MANUAL", "Manual Validation"


class AutomationTimesheet(models.Model):
    timesheet_number = models.IntegerField()
    type = models.CharField(
        max_length=10, choices=TimesheetType.choices, default=TimesheetType.AUTO
    )
    month = models.DateField(
        max_length=3, choices=MonthChoices.choices, default=MonthChoices.JANUARY
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    result = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Automation Timesheet - {self.timesheet_number}"

    class Meta:
        app_label = "hr_management"
        db_table = "automation_timesheet"
