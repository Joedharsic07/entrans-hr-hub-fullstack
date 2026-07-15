from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from hr_management.services.analytics_service import AnalyticsService

class AnalyticsDashboardView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        data = AnalyticsService.get_dashboard_data()
        return Response(data)
