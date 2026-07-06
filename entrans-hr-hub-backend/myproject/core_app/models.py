from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
import datetime
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100, blank=True, default="")
    last_name = models.CharField(max_length=100, blank=True, default="")
    designation = models.CharField(max_length=150, blank=True, default="")
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    password_expires_at = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.name

    class Meta:
        db_table = "user"


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "project"


class UserProject(models.Model):
    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("collaborator", "Collaborator"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="collaborator")

    def __str__(self):
        return f"{self.user.name} - {self.project.name} ({self.role})"

    class Meta:
        db_table = "user_project"
        unique_together = ("user", "project")


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
        db_table = "timesheet"


class HolidayWeekend(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description

    class Meta:
        db_table = "holiday_weekend"


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
        db_table = "automation_timesheet"


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
        db_table = "timesheet_email_log"


class UserAccessLog(models.Model):
    ACTION_CHOICES = [
        ("login", "Login"),
        ("logout", "Logout"),
        ("password_change", "Password Change"),
        ("password_reset", "Password Reset"),
    ]
    STATUS_CHOICES = [
        ("success", "Success"),
        ("failed", "Failed"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="access_logs")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, default="login")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="success")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_access_log"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.timestamp} "


class PPTGenerationLog(models.Model):
    employee_name = models.CharField(max_length=255)
    years_of_service = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.employee_name} ({self.years_of_service}) - {self.created_at}"

    class Meta:
        db_table = "ppt_generation_log"
        ordering = ["-created_at"]
