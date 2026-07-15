from django.db import transaction
from django.db.models import Q, Sum
from hr_management.repositories.project_repository import ProjectRepository, UserProjectRepository
from hr_management.repositories.user_repository import UserRepository
from hr_management.models.timesheet import Timesheet
from hr_management.models.project import Project, UserProject

class ProjectService:
    @staticmethod
    def get_user_projects_list(user, target_user_id=None):
        target_user = user
        if target_user_id:
            target_user = UserRepository.get_by_id(target_user_id)
            if not target_user:
                raise ValueError("User not found")
            if not (user.is_staff or user.id == target_user.id):
                raise PermissionError("You don't have permission to view this user's projects")

        user_projects = UserProjectRepository.get_user_projects(target_user)
        user_project_map = {up.project_id: up for up in user_projects}
        projects = [up.project for up in user_projects]

        return projects, user_project_map

    @staticmethod
    def create_or_update_project(data, owner_id):
        owner = UserRepository.get_by_id(owner_id)
        if not owner:
            raise ValueError("Owner not found")

        project_name = data.get("name")
        existing_project = ProjectRepository.get_by_name(project_name)
        user_projects_data = data.pop("user_projects", [])

        if existing_project:
            added_users = []
            for entry in user_projects_data:
                target_user = UserRepository.get_by_id(entry.get("user"))
                if target_user:
                    role = entry.get("role", "collaborator")
                    if role in ["owner", "collaborator"]:
                        if not UserProjectRepository.assignment_exists(target_user, existing_project):
                            UserProject.objects.create(user=target_user, project=existing_project, role=role)
                            added_users.append(target_user.id)
            
            return existing_project, added_users, True

        with transaction.atomic():
            project = Project.objects.create(
                name=data.get("name"),
                description=data.get("description"),
                owner=owner
            )
            UserProject.objects.create(user=owner, project=project, role="owner")
            assigned_user_ids = {owner.id}

            for entry in user_projects_data:
                target_user = UserRepository.get_by_id(entry.get("user"))
                if target_user:
                    role = entry.get("role", "collaborator")
                    if role in ["owner", "collaborator"] and target_user.id not in assigned_user_ids:
                        UserProject.objects.create(user=target_user, project=project, role=role)
                        assigned_user_ids.add(target_user.id)

            return project, list(assigned_user_ids), False

    @staticmethod
    def get_project_for_user(pk, user):
        project = ProjectRepository.get_by_id(pk)
        if project and (project.owner == user or UserProjectRepository.assignment_exists(user, project)):
            return project
        return None

    @staticmethod
    def delete_project(pk, user):
        project = ProjectService.get_project_for_user(pk, user)
        if not project:
            raise ValueError("Project not found or access denied")
        if project.owner != user:
            raise PermissionError("Only the project owner can delete the project")
        project.delete()

    @staticmethod
    def get_user_project_assignments(user, project_id=None, user_id=None):
        owned_projects = ProjectRepository.get_owned_projects(user)
        queryset = UserProjectRepository.get_user_projects(user) | UserProjectRepository.get_all().filter(project__in=owned_projects)
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        return queryset.distinct()

    @staticmethod
    def assign_user_to_project(user, project_id, target_user_id, role="collaborator"):
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")

        if not (user.is_staff or user.is_superuser) and project.owner != user:
            raise PermissionError("Only the project owner or an admin can add users to this project")

        if UserProjectRepository.assignment_exists(target_user_id, project_id):
            raise ValueError("This user is already assigned to this project")

        target_user = UserRepository.get_by_id(target_user_id)
        if not target_user:
            raise ValueError("Target user not found")

        return UserProject.objects.create(user=target_user, project=project, role=role)

    @staticmethod
    def get_assignment_for_user(pk, user):
        user_project = UserProjectRepository.get_by_id(pk)
        if user_project and (user_project.user == user or user_project.project.owner == user):
            return user_project
        return None

    @staticmethod
    def remove_assignment(pk, user):
        user_project = ProjectService.get_assignment_for_user(pk, user)
        if not user_project:
            raise ValueError("User-Project assignment not found or access denied")
        if user_project.project.owner != user:
            raise PermissionError("Only the project owner can remove users from the project")
        user_project.delete()

    @staticmethod
    def get_project_user_roles(project_search, user_search, page, page_size):
        projects = ProjectRepository.get_all_projects().prefetch_related("userproject_set", "userproject_set__user").order_by("name")

        if project_search:
            projects = projects.filter(name__icontains=project_search)

        total_count = projects.count()
        total_pages = max(1, (total_count + page_size - 1) // page_size)
        page = min(page, total_pages)
        offset = (page - 1) * page_size
        projects_page = projects[offset : offset + page_size]

        results = []
        for project in projects_page:
            assignments = UserProjectRepository.get_project_users(project)
            if user_search:
                assignments = assignments.filter(
                    Q(user__name__icontains=user_search)
                    | Q(user__email__icontains=user_search)
                    | Q(role__icontains=user_search)
                )
            assignments = assignments.order_by("role", "user__name")
            users = [
                {
                    "user_id": up.user.id,
                    "user_name": up.user.name,
                    "email": up.user.email,
                    "role": up.role,
                }
                for up in assignments
            ]
            results.append(
                {
                    "project_id": project.id,
                    "project_name": project.name,
                    "user_count": UserProjectRepository.get_project_users(project).count(),
                    "users": users,
                }
            )

        return total_count, total_pages, page, results

    @staticmethod
    def get_project_users_detail(project_id, user_search, page, page_size):
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")

        assignments = UserProjectRepository.get_project_users(project)
        if user_search:
            assignments = assignments.filter(
                Q(user__name__icontains=user_search)
                | Q(user__email__icontains=user_search)
                | Q(role__icontains=user_search)
            )
        assignments = assignments.order_by("role", "user__name")

        total_count = assignments.count()
        total_pages = max(1, (total_count + page_size - 1) // page_size)
        page = min(page, total_pages)
        offset = (page - 1) * page_size
        assignments_page = assignments[offset : offset + page_size]

        users = [
            {
                "user_project_id": up.id,
                "user_id": up.user.id,
                "user_name": up.user.name,
                "email": up.user.email,
                "designation": up.user.designation,
                "role": up.role,
            }
            for up in assignments_page
        ]

        total_duration_agg = Timesheet.objects.filter(user_project__project=project).aggregate(total=Sum('duration'))
        total_duration = total_duration_agg['total'] or 0

        return project, total_duration, total_count, total_pages, page, users
