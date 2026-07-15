import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from hr_management.serializers.timesheet import TimesheetSerializer
from hr_management.services.timesheet_service import TimesheetService
from common.jwt_utils import get_user_from_request
from hr_management.repositories.project_repository import UserProjectRepository

logger = logging.getLogger(__name__)

class TimesheetListCreateView(APIView):
    """List all timesheets or create a new timesheet"""

    def get(self, request):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        timesheets, month, year = TimesheetService.get_timesheets(user, request.query_params)
        serializer = TimesheetSerializer(timesheets, many=True)
        raw_data = serializer.data

        total_duration, leave_days = TimesheetService.calculate_statistics(timesheets)
        validated_data, summary_data, val_error = TimesheetService.validate_timesheet_data(raw_data)

        if val_error:
            return Response({"error": "Validation failed", "details": val_error}, status=500)

        if month and year:
            raw_data = TimesheetService.fill_missing_dates(raw_data, month, year)

        status_map = {
            (entry.get("Date"), entry.get("Hours")): entry.get("Status", "")
            for entry in validated_data
        }

        for ts in raw_data:
            date_val = ts.get("date")
            hours = str(ts.get("duration", ""))
            if "Status" not in ts:
                ts["Status"] = status_map.get((date_val, hours), "")

        return Response(
            {
                "timesheets": raw_data,
                "validated_data": validated_data,
                "validation_summary": summary_data,
                "statistics": {
                    "total_duration": total_duration,
                    "leave_days": leave_days,
                },
            }
        )

    def post(self, request):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        user_project_id = request.data.get("user_project")
        user_project = UserProjectRepository.get_by_id(user_project_id)
        
        if not user_project:
            return Response(
                {"error": "User-Project assignment not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
            
        if user_project.user.id != user.id and not (user.is_staff or user.is_superuser):
            return Response(
                {"error": "You can only create timesheets for your own project assignments"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TimesheetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TimesheetDetailView(APIView):
    """Retrieve, update, or delete a timesheet instance"""

    def get(self, request, pk):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        timesheet = TimesheetService.get_timesheet_for_user(pk, user)
        if not timesheet:
            return Response(
                {"error": "Timesheet not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(TimesheetSerializer(timesheet).data)

    def patch(self, request, pk):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        timesheet = TimesheetService.get_timesheet_for_user(pk, user)
        if not timesheet:
            return Response(
                {"error": "Timesheet not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_project_id = request.data.get("user_project")
        if user_project_id:
            user_project = UserProjectRepository.get_by_id(user_project_id)
            if not user_project:
                return Response(
                    {"error": "User-Project assignment not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if not (user.is_staff or user.is_superuser) and user_project.user.id != user.id:
                return Response(
                    {"error": "You can only assign timesheets to your own project assignments"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        status_value = request.data.get("status")
        if status_value:
            if status_value.lower() == "half day":
                request.data["day_count"] = 0.5
            elif status_value.lower() == "leave":
                request.data["day_count"] = 1
            elif status_value.lower() == "present":
                request.data["day_count"] = 1

        serializer = TimesheetSerializer(timesheet, data=request.data, partial=True)
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
            TimesheetService.delete_timesheet(pk, user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_404_NOT_FOUND)

class UserTimesheetListView(APIView):
    """Simple list of users with their projects and links to timesheets"""

    def get(self, request):
        requesting_user = get_user_from_request(request)
        if not requesting_user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response_data = TimesheetService.get_user_timesheet_list(requesting_user)
        
        if not requesting_user.is_staff and response_data:
            return Response(response_data[0])

        return Response(response_data)

class TimesheetAPIView(APIView):
    def get(self, request):
        user = get_user_from_request(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        timesheets, month, year = TimesheetService.get_timesheets(user, request.query_params)
        serializer = TimesheetSerializer(timesheets, many=True)
        timesheet_data = serializer.data

        total_duration, leave_days = TimesheetService.calculate_statistics(timesheets)
        
        validated_records = []
        summary = []
        if timesheet_data:
            validated_records, summary, val_error = TimesheetService.validate_timesheet_data(timesheet_data)
            if val_error:
                return Response({"error": "Validation failed", "details": val_error})

        return Response(
            {
                "timesheets": timesheet_data,
                "validated_timesheets": validated_records,
                "validation_summary": summary,
                "statistics": {
                    "total_duration": total_duration,
                    "leave_days": leave_days,
                },
            },
            status=200,
        )

class ValidateMultipleTimesheetView(APIView):
    def get(self, request):
        requesting_user = get_user_from_request(request)
        if not requesting_user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        month = request.query_params.get("month")
        year = request.query_params.get("year")
        if not month or not year:
            return Response(
                {"error": "month and year are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response(
                {"error": "Invalid month or year format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = TimesheetService.get_multiple_validation_status(requesting_user, month, year)
        return Response(response_data)

    def post(self, request):
        user = get_user_from_request(request)
        if not user or not (user.is_staff or user.is_superuser):
            return Response(
                {"error": "Admin access required."}, status=status.HTTP_403_FORBIDDEN
            )

        user_project_map = request.data.get("user_project_map", {})
        month = request.data.get("month")
        year = request.data.get("year")

        if not user_project_map or not month or not year:
            return Response(
                {"error": "user_project_map, month, and year are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({"error": "Invalid month or year format."}, status=400)

        result_data = TimesheetService.run_multiple_validations(user, month, year, user_project_map)
        
        if "error" in result_data and len(result_data) == 1:
            return Response(result_data, status=500)
            
        return Response(result_data, status=200)

class PushTimesheetEmailView(APIView):
    def post(self, request):
        user = get_user_from_request(request)
        if not user or not (user.is_staff or user.is_superuser):
            return Response(
                {"error": "Admin access required."}, status=status.HTTP_403_FORBIDDEN
            )

        user_project_map = request.data.get("user_project_map")
        month = request.data.get("month")
        year = request.data.get("year")

        if not user_project_map or not month or not year:
            return Response(
                {"error": "user_project_map, month, and year are required."}, status=400
            )

        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return Response({"error": "Month and year must be integers."}, status=400)

        try:
            sent, failed = TimesheetService.send_timesheet_emails(user, month, year, user_project_map)
            return Response(
                {
                    "sent": sent,
                    "failed": failed,
                },
                status=200 if not failed else 207,
            )
        except ValueError as ve:
            return Response({"error": str(ve)}, status=404)

class TimesheetReminderView(APIView):
    """
    POST /api/send-timesheet-reminders/
    Admin-only manual trigger for the same logic the cron job runs automatically
    on the 18th of each month at 18:00.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        requesting_user = get_user_from_request(request)
        if not requesting_user or not (
            requesting_user.is_staff or requesting_user.is_superuser
        ):
            return Response(
                {"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            dry_run = request.data.get("dry_run", False)
            result = TimesheetService.trigger_reminders(dry_run=bool(dry_run))
            return Response(
                {
                    "status": "success",
                    "message": (
                        f"Reminder run complete — "
                        f"sent: {result['emails_sent']}, "
                        f"skipped (no missing days): {result['emails_skipped']}, "
                        f"failed: {result['emails_failed']}"
                    ),
                    **result,
                }
            )
        except Exception as e:
            logger.error(f"Timesheet reminder trigger error: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
