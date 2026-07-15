from rest_framework import generics, permissions, status
from rest_framework.response import Response
from hr_management.serializers.attendance import AttendanceLogSerializer
from hr_management.services.attendance_service import AttendanceService
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError

class AttendanceLogListView(generics.ListAPIView):
    serializer_class = AttendanceLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AttendanceService.get_logs(self.request.user)

class ClockInView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        lat = request.data.get("latitude")
        lng = request.data.get("longitude")
        
        try:
            log = AttendanceService.clock_in(request.user, lat, lng)
            return Response(AttendanceLogSerializer(log).data)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)

class ClockOutView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        lat = request.data.get("latitude")
        lng = request.data.get("longitude")
        
        try:
            log = AttendanceService.clock_out(request.user, lat, lng)
            return Response(AttendanceLogSerializer(log).data)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
