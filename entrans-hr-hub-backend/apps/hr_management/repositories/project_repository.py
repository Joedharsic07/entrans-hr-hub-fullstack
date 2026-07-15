from hr_management.models.project import Project, UserProject
from django.db.models import QuerySet

class ProjectRepository:
    @staticmethod
    def get_by_id(project_id) -> Project | None:
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return None

    @staticmethod
    def get_by_name(name: str) -> Project | None:
        return Project.objects.filter(name=name).first()

    @staticmethod
    def get_owned_projects(user) -> QuerySet:
        return Project.objects.filter(owner=user)

    @staticmethod
    def get_all_projects() -> QuerySet:
        return Project.objects.all()

class UserProjectRepository:
    @staticmethod
    def get_by_id(user_project_id) -> UserProject | None:
        try:
            return UserProject.objects.get(id=user_project_id)
        except UserProject.DoesNotExist:
            return None

    @staticmethod
    def get_user_projects(user) -> QuerySet:
        return UserProject.objects.filter(user=user).select_related("project")

    @staticmethod
    def get_project_users(project) -> QuerySet:
        return UserProject.objects.filter(project=project).select_related("user")

    @staticmethod
    def get_assignment(user, project) -> UserProject | None:
        return UserProject.objects.filter(user=user, project=project).first()

    @staticmethod
    def assignment_exists(user, project) -> bool:
        return UserProject.objects.filter(user=user, project=project).exists()

    @staticmethod
    def get_all() -> QuerySet:
        return UserProject.objects.all()
