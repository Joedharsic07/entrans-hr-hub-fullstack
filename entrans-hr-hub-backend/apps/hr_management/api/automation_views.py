import os
import math
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse
from hr_management.serializers import PPTGenerationLogSerializer, UploadExcelSerializer, UploadTimesheetSerializer, GenerateTemplateSerializer, EmailSerializer
from hr_management.models import PPTGenerationLog
from hr_management.services.automation_service import AutomationService
from common.jwt_utils import get_user_from_request

def sanitize_nans(obj):
    if isinstance(obj, dict):
        return {k: sanitize_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_nans(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj

class PPTAutomationAPI(APIView):
    def get(self, request):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        logs = PPTGenerationLog.objects.all()[:50]
        return Response(PPTGenerationLogSerializer(logs, many=True).data)

    def post(self, request):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = UploadExcelSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            excel_file = request.FILES.get("file")
            output_path = AutomationService.generate_ppt(user, serializer.validated_data, excel_file)
            return FileResponse(open(output_path, "rb"), filename="Anniversary_Slides.pptx")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TimeTrackingAPI(APIView):
    def post(self, request):
        serializer = UploadTimesheetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            timesheet_file = request.FILES["timesheet_file"]
            validation_type = serializer.validated_data.get("validation_type", "standard")
            
            new_file_name, validated_sheets, summary_data = AutomationService.process_time_tracking(
                timesheet_file, validation_type
            )

            response_data = {
                "file_name": new_file_name,
                "validated_data": validated_sheets,
                "validation_summary": summary_data,
                "success": True,
            }

            return Response(sanitize_nans(response_data))

        except ValueError as ve:
            return Response(
                {"status": "Invalid", "flag": str(ve)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"status": "Invalid", "flag": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class TimeTrackingTemplateAPI(APIView):
    def post(self, request):
        serializer = GenerateTemplateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            month = serializer.validated_data.get("month")
            year = serializer.validated_data.get("year")

            user_name = "User"
            if request.user.is_authenticated:
                user_name = request.user.name.split()[0] if getattr(request.user, "name", None) else request.user.first_name
                if not user_name:
                    user_name = "User"

            template_path = AutomationService.generate_time_tracking_template(month, year, user_name)

            return Response(
                {
                    "success": True,
                    "template_path": os.path.basename(template_path),
                    "download_url": f"/api/time-tracking/templates/{os.path.basename(template_path)}/",
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, filename):
        template_path = os.path.join(settings.MEDIA_ROOT, "time_tracking_outputs", filename)

        if os.path.exists(template_path):
            return FileResponse(open(template_path, "rb"), filename=filename)
        return Response({"error": "Template file not found"}, status=status.HTTP_404_NOT_FOUND)

class TimeTrackingEmailAPI(APIView):
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        recipient_email = serializer.validated_data["recipient_email"]
        json_data = serializer.validated_data["json_data"]
        sender = request.user if request.user.is_authenticated else None

        try:
            success, flag_count = AutomationService.send_time_tracking_email(sender, recipient_email, json_data)

            if success:
                return Response({
                    "success": True,
                    "message": f"Sent {flag_count} flagged entries to {recipient_email}",
                })
            else:
                return Response(
                    {"success": False, "error": "Failed to send flagged entries"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
