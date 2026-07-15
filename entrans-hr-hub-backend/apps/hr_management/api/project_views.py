import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from hr_management.serializers.project import ProjectSerializer, UserProjectSerializer
from hr_management.services.project_service import ProjectService
from common.jwt_utils import get_user_from_request

logger = logging.getLogger(__name__)

class ProjectListCreateView(APIView):
    """List all projects the user is involved in, or create a new project."""

    def get(self, request, user_id=None):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            projects, user_project_map = ProjectService.get_user_projects_list(user, user_id)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as pe:
            return Response({"error": str(pe)}, status=status.HTTP_403_FORBIDDEN)

        response_data = []
        for project in projects:
            project_data = ProjectSerializer(project).data
            user_project = user_project_map.get(project.id)
            project_data["user_project_id"] = user_project.id if user_project else None
            project_data["role"] = user_project.role if user_project else None
            response_data.append(project_data)

        return Response(response_data)

    def post(self, request):
        user = get_user_from_request(request)
        if not user or not user.is_staff:
            return Response(
                {"error": "Only admin can create or modify projects"},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()
        owner_id = data.get("owner")

        if not owner_id:
            return Response(
                {"error": "Missing 'owner' field"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project, added_users, is_existing = ProjectService.create_or_update_project(data, owner_id)
            if is_existing:
                return Response(
                    {
                        "message": f"Users added to existing project '{project.name}'",
                        "project_id": project.id,
                        "added_user_ids": added_users,
                    },
                    status=status.HTTP_200_OK,
                )
            
            serializer = ProjectSerializer(project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProjectDetailView(APIView):
    """Retrieve, update, or delete a project instance"""

    def get(self, request, pk):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        project = ProjectService.get_project_for_user(pk, user)
        if not project:
            return Response(
                {"error": "Project not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ProjectSerializer(project).data)

    def patch(self, request, pk):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        project = ProjectService.get_project_for_user(pk, user)
        if not project:
            return Response(
                {"error": "Project not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if project.owner != user:
            return Response(
                {"error": "Only the project owner can update project details"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            ProjectService.delete_project(pk, user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as pe:
            return Response({"error": str(pe)}, status=status.HTTP_403_FORBIDDEN)

class UserProjectListCreateView(APIView):
    """List all user-project assignments or create a new assignment"""

    def get(self, request):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        project_id = request.query_params.get("project_id")
        user_id = request.query_params.get("user_id")
        
        queryset = ProjectService.get_user_project_assignments(user, project_id, user_id)
        serializer = UserProjectSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        project_id = request.data.get("project")
        target_user_id = request.data.get("user")
        role = request.data.get("role", "collaborator")

        try:
            assignment = ProjectService.assign_user_to_project(user, project_id, target_user_id, role)
            serializer = UserProjectSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as ve:
            if str(ve) == "Project not found":
                return Response({"error": str(ve)}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionError as pe:
            return Response({"error": str(pe)}, status=status.HTTP_403_FORBIDDEN)

class UserProjectDetailView(APIView):
    """Retrieve, update, or delete a user-project assignment"""

    def get(self, request, pk):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_project = ProjectService.get_assignment_for_user(pk, user)
        if not user_project:
            return Response(
                {"error": "User-Project assignment not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(UserProjectSerializer(user_project).data)

    def patch(self, request, pk):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_project = ProjectService.get_assignment_for_user(pk, user)
        if not user_project:
            return Response(
                {"error": "User-Project assignment not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user_project.project.owner != user:
            return Response(
                {"error": "Only the project owner can modify project assignments"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if "project" in request.data and request.data["project"] != user_project.project.id:
            return Response(
                {"error": "Cannot change project association for an existing assignment"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UserProjectSerializer(user_project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            ProjectService.remove_assignment(pk, user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as pe:
            return Response({"error": str(pe)}, status=status.HTTP_403_FORBIDDEN)

class ProjectUserRolesView(APIView):
    """Admin-only: Paginated project list with optional project name and user search filters."""

    def get(self, request):
        user = get_user_from_request(request)
        if not user or not (user.is_staff or user.is_superuser):
            return Response(
                {"error": "Admin access required."}, status=status.HTTP_403_FORBIDDEN
            )

        project_search = request.query_params.get("project_search", "").strip()
        user_search = request.query_params.get("user_search", "").strip()

        try:
            page = max(1, int(request.query_params.get("page", 1)))
            page_size = min(50, max(1, int(request.query_params.get("page_size", 10))))
        except (ValueError, TypeError):
            page, page_size = 1, 10

        total_count, total_pages, page, results = ProjectService.get_project_user_roles(
            project_search, user_search, page, page_size
        )

        return Response(
            {
                "count": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "results": results,
            },
            status=status.HTTP_200_OK,
        )

class ProjectUsersView(APIView):
    """Admin-only: Paginated user list for a specific project with optional user search filter."""

    def get(self, request, project_id):
        user = get_user_from_request(request)
        if not user or not (user.is_staff or user.is_superuser):
            return Response(
                {"error": "Admin access required."}, status=status.HTTP_403_FORBIDDEN
            )

        user_search = request.query_params.get("user_search", "").strip()

        try:
            page = max(1, int(request.query_params.get("page", 1)))
            page_size = min(50, max(1, int(request.query_params.get("page_size", 12))))
        except (ValueError, TypeError):
            page, page_size = 1, 12

        try:
            project, total_duration, total_count, total_pages, page, users = ProjectService.get_project_users_detail(
                project_id, user_search, page, page_size
            )
            return Response(
                {
                    "project_id": project.id,
                    "project_name": project.name,
                    "project_description": project.description,
                    "total_duration": float(total_duration),
                    "count": total_count,
                    "total_pages": total_pages,
                    "current_page": page,
                    "page_size": page_size,
                    "users": users,
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_404_NOT_FOUND)
