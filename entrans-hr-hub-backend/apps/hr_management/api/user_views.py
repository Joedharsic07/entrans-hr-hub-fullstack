import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from hr_management.serializers.user import UserSerializer
from hr_management.services.user_service import UserService
from common.jwt_utils import get_user_from_request
from common.helpers import parse_user_agent
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

class UserListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        User = get_user_model()
        users = User.objects.all().values("id", "name", "email")
        return Response(users)

class MeView(APIView):
    def get(self, request):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = UserSerializer(user)
        data = dict(serializer.data)
        
        profile_data = UserService.get_user_profile(user)
        data.update(profile_data)

        return Response(data)

    def put(self, request):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        first_name = request.data.get("first_name", user.first_name)
        last_name = request.data.get("last_name", user.last_name)
        designation = request.data.get("designation", user.designation)

        updated_user = UserService.update_profile(user, first_name, last_name, designation)

        serializer = UserSerializer(updated_user)
        return Response({
            "status": "success",
            "message": "Profile updated successfully.",
            "user": serializer.data
        })

class CreateUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        requesting_user = get_user_from_request(request)
        if not requesting_user or not requesting_user.is_superuser:
            return Response(
                {"error": "Super admin access required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        email = request.data.get("email", "").strip().lower()
        first_name = request.data.get("first_name", "").strip()
        last_name = request.data.get("last_name", "").strip()
        role = request.data.get("role", "user")
        designation = request.data.get("designation", "").strip()
        date_of_joining = request.data.get("date_of_joining", "").strip()

        if not email or not first_name or not last_name or not date_of_joining:
            return Response(
                {"error": "email, first_name, last_name, and date_of_joining are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if role not in ("user", "superadmin"):
            return Response(
                {"error": "role must be 'user' or 'superadmin'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            UserService.create_user(email, first_name, last_name, role, designation, date_of_joining)
            return Response(
                {
                    "status": "success",
                    "message": f"User created and credentials sent to {email}",
                },
                status=status.HTTP_201_CREATED,
            )
        except ValueError as ve:
            return Response(
                {"error": str(ve)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Create user error: {str(e)}")
            return Response(
                {"error": "Failed to create user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class UserAdminView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        requesting_user = get_user_from_request(request)
        if not requesting_user or not (
            requesting_user.is_staff or requesting_user.is_superuser
        ):
            return Response(
                {"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN
            )

        search = request.query_params.get("search", "").strip()

        try:
            page = max(1, int(request.query_params.get("page", 1)))
            page_size = min(50, max(1, int(request.query_params.get("page_size", 15))))
        except (ValueError, TypeError):
            page, page_size = 1, 15

        users, total, total_pages, active_count, roles_count, projects_by_user = UserService.get_users_list(search, page, page_size)

        data = [
            {
                "id": u.id,
                "user_id": str(u.user_id),
                "name": u.name,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "email": u.email,
                "designation": u.designation,
                "role": "Admin" if (u.is_staff or u.is_superuser) else "User",
                "is_active": u.is_active,
                "projects": projects_by_user.get(u.id, []),
            }
            for u in users
        ]

        return Response(
            {
                "count": total,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "active_count": active_count,
                "roles_count": roles_count,
                "users": data,
            }
        )

class UserAdminDetailView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, user_id):
        requesting_user = get_user_from_request(request)
        if not requesting_user or not (
            requesting_user.is_staff or requesting_user.is_superuser
        ):
            return Response(
                {"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            target = UserService.update_user_admin(user_id, requesting_user.id, request.data)
            return Response(
                {
                    "id": target.id,
                    "is_active": target.is_active,
                    "message": "User updated successfully",
                }
            )
        except ValueError as ve:
            if str(ve) == "User not found":
                return Response({"error": str(ve)}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        requesting_user = get_user_from_request(request)
        if not requesting_user or not (
            requesting_user.is_staff or requesting_user.is_superuser
        ):
            return Response(
                {"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            UserService.delete_user(user_id, requesting_user.id)
            return Response(
                {"message": "User deleted successfully"}, status=status.HTTP_200_OK
            )
        except ValueError as ve:
            if str(ve) == "User not found":
                return Response({"error": str(ve)}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)

class UserAccessLogView(APIView):
    def get(self, request):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        logs = user.access_logs.all()[:50]
        data = [
            {
                "id": log.id,
                "action": log.action,
                "status": log.status,
                "ip_address": log.ip_address,
                "device": parse_user_agent(log.user_agent),
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ]
        return Response(data)

class UserRecentActivityView(APIView):
    def get(self, request):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        from django.utils import timezone
        from datetime import timedelta
        
        one_week_ago = timezone.now() - timedelta(days=7)
        one_week_ago_date = timezone.now().date() - timedelta(days=7)

        activities = []

        # Access Logs
        access_logs = user.access_logs.filter(timestamp__gte=one_week_ago).order_by('-timestamp')[:10]
        for log in access_logs:
            activities.append({
                "action": "Login" if log.action == "login" else log.action.replace("_", " ").title(),
                "timestamp": log.timestamp.isoformat(),
                "status": log.status,
                "timestamp_obj": log.timestamp
            })

        # Timesheets
        from hr_management.models.timesheet import Timesheet
        timesheets = Timesheet.objects.filter(user_project__user=user, updated_at__gte=one_week_ago).order_by('-updated_at')[:5]
        for ts in timesheets:
            activities.append({
                "action": "Timesheet Submitted",
                "timestamp": ts.updated_at.isoformat(),
                "status": "success",
                "timestamp_obj": ts.updated_at
            })

        # Leaves
        from hr_management.models.leave import LeaveRequest
        leaves = LeaveRequest.objects.filter(employee=user, applied_on__gte=one_week_ago).order_by('-applied_on')[:5]
        for leave in leaves:
            activities.append({
                "action": "Leave Applied",
                "timestamp": leave.applied_on.isoformat(),
                "status": "success" if leave.status in ["pending", "approved"] else "failed",
                "timestamp_obj": leave.applied_on
            })
            
        # Attendance Logs
        from hr_management.models.attendance import AttendanceLog
        attendance_logs = AttendanceLog.objects.filter(employee=user, date__gte=one_week_ago_date).order_by('-date')[:5]
        for att in attendance_logs:
            timestamp_obj = att.clock_in if att.clock_in else None
            # fallback to start of day if clock in missing but somehow we want to show it
            if not timestamp_obj:
                from datetime import datetime, time
                timestamp_obj = timezone.make_aware(datetime.combine(att.date, time.min))
                
            activities.append({
                "action": "Clocked In",
                "timestamp": timestamp_obj.isoformat() if hasattr(timestamp_obj, 'isoformat') else str(timestamp_obj),
                "status": "success",
                "timestamp_obj": timestamp_obj
            })

        # Sort and limit
        # Ensure timestamp_obj has timezone to compare
        for act in activities:
            if act["timestamp_obj"] and timezone.is_naive(act["timestamp_obj"]):
                act["timestamp_obj"] = timezone.make_aware(act["timestamp_obj"])

        activities = [a for a in activities if a["timestamp_obj"] is not None]
        activities.sort(key=lambda x: x["timestamp_obj"], reverse=True)
        top_activities = activities[:10]
        
        for act in top_activities:
            del act["timestamp_obj"]
            
        return Response(top_activities)
