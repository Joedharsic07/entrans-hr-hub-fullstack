from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from hr_management.services.admin_dashboard_service import AdminDashboardService
from common.jwt_utils import get_user_from_request

class AdminDashboardStatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        requesting_user = get_user_from_request(request)
        if not requesting_user or not (requesting_user.is_staff or requesting_user.is_superuser):
            return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)
        
        return Response(AdminDashboardService.get_stats())

class AdminRecentActivityView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        requesting_user = get_user_from_request(request)
        if not requesting_user or not (requesting_user.is_staff or requesting_user.is_superuser):
            return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)
        
        return Response(AdminDashboardService.get_recent_activities())

class AdminUpcomingAnniversariesView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        requesting_user = get_user_from_request(request)
        if not requesting_user or not (requesting_user.is_staff or requesting_user.is_superuser):
            return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)
        
        return Response(AdminDashboardService.get_upcoming_anniversaries())
