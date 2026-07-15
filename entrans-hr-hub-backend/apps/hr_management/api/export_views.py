from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import permissions
from hr_management.services.export_service import ExportService

class ExportAttendanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        format_type = request.query_params.get('format', 'csv').lower()

        if format_type == 'excel':
            buffer = ExportService.export_attendance_excel(request.user)
            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="attendance.xlsx"'
            return response
            
        elif format_type == 'pdf':
            buffer = ExportService.export_attendance_pdf(request.user)
            return HttpResponse(buffer, content_type='application/pdf')
            
        else:
            buffer = ExportService.export_attendance_csv(request.user)
            response = HttpResponse(buffer.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="attendance.csv"'
            return response

class ExportLeaveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        buffer = ExportService.export_leaves_csv(request.user)
        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="leaves.csv"'
        return response
