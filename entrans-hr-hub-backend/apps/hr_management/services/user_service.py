import string
import secrets
from django.db.models import Q
from django.utils.timezone import now
from datetime import timedelta
from hr_management.repositories.user_repository import UserRepository
from hr_management.models.project import UserProject
from common.email_service import EmailService

class UserService:
    @staticmethod
    def get_user_profile(user):
        user_projects = UserProject.objects.filter(user=user).select_related("project")
        projects = [
            {
                "user_project_id": up.id,
                "project_id": up.project.id,
                "project_name": up.project.name,
                "role": up.role,
            }
            for up in user_projects
        ]
        
        return {
            "projects": projects,
            "projects_count": len(projects)
        }

    @staticmethod
    def update_profile(user, first_name, last_name, designation):
        user.first_name = first_name
        user.last_name = last_name
        user.name = f"{first_name} {last_name}".strip()
        if designation is not None:
            user.designation = designation
            
        user.save()
        return user

    @staticmethod
    def generate_temp_password(length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def create_user(email, first_name, last_name, role, designation, date_of_joining):
        if UserRepository.exists_by_email(email):
            raise ValueError("A user with this email already exists")

        temp_password = UserService.generate_temp_password()
        expires_at = now() + timedelta(hours=24)

        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        new_user = UserModel.objects.create_user(
            email=email,
            name=f"{first_name} {last_name}",
            password=temp_password,
        )
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.designation = designation
        new_user.password_expires_at = expires_at
        if date_of_joining:
            new_user.date_of_joining = date_of_joining

        if role == "superadmin":
            new_user.is_staff = True
            new_user.is_superuser = True

        new_user.save()

        EmailService().send_welcome_email_with_temp_password(
            email, first_name, temp_password
        )
        return new_user

    @staticmethod
    def get_users_list(search, page, page_size):
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        
        queryset = UserModel.objects.all().order_by("name")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(email__icontains=search)
                | Q(designation__icontains=search)
            )

        total = queryset.count()
        total_pages = max(1, (total + page_size - 1) // page_size)
        offset = (page - 1) * page_size
        users = queryset[offset : offset + page_size]

        user_ids = [u.id for u in users]
        user_projects = (
            UserProject.objects.filter(user_id__in=user_ids)
            .select_related("project")
            .values("user_id", "project__id", "project__name", "role")
        )
        
        projects_by_user = {}
        for up in user_projects:
            projects_by_user.setdefault(up["user_id"], []).append(
                {
                    "project_id": up["project__id"],
                    "project_name": up["project__name"],
                    "role": up["role"],
                }
            )

        active_count = UserModel.objects.filter(is_active=True).count()
        roles_count = 2

        return users, total, total_pages, active_count, roles_count, projects_by_user

    @staticmethod
    def update_user_admin(user_id, requesting_user_id, data):
        target = UserRepository.get_by_id(user_id)
        if not target:
            raise ValueError("User not found")

        if "is_active" in data:
            if target.id == requesting_user_id:
                raise ValueError("You cannot deactivate your own account")
            target.is_active = bool(data["is_active"])
            
        if "first_name" in data or "last_name" in data:
            first_name = data.get("first_name", target.first_name)
            last_name = data.get("last_name", target.last_name)
            target.first_name = first_name
            target.last_name = last_name
            target.name = f"{first_name} {last_name}".strip()

        if "designation" in data:
            target.designation = data["designation"]

        if "role" in data:
            new_role = data["role"]
            if new_role == "superadmin":
                target.is_staff = True
                target.is_superuser = True
            elif new_role == "user":
                target.is_staff = False
                target.is_superuser = False

        target.save()
        return target

    @staticmethod
    def delete_user(user_id, requesting_user_id):
        target = UserRepository.get_by_id(user_id)
        if not target:
            raise ValueError("User not found")
        if target.id == requesting_user_id:
            raise ValueError("You cannot delete your own account")
        target.delete()
        return True
