from django.db import models
from .user import User

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")

    def __str__(self):
        return self.name

    class Meta:
        app_label = "hr_management"
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
        app_label = "hr_management"
        db_table = "user_project"
        unique_together = ("user", "project")
