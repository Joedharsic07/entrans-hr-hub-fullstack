from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
import uuid

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
        app_label = "hr_management"
        db_table = "user"


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
        app_label = "hr_management"
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
        app_label = "hr_management"
        db_table = "ppt_generation_log"
        ordering = ["-created_at"]
