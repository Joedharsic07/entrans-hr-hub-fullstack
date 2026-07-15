from hr_management.models.attendance import AttendanceLog
from django.db.models import QuerySet

class AttendanceRepository:
    @staticmethod
    def get_all_logs() -> QuerySet:
        return AttendanceLog.objects.all().order_by('-date')

    @staticmethod
    def get_user_logs(user) -> QuerySet:
        return AttendanceLog.objects.filter(employee=user).order_by('-date')

    @staticmethod
    def get_log_for_today(user, today) -> tuple[AttendanceLog, bool]:
        return AttendanceLog.objects.get_or_create(employee=user, date=today)

    @staticmethod
    def get_log_by_date(user, date) -> AttendanceLog | None:
        try:
            return AttendanceLog.objects.get(employee=user, date=date)
        except AttendanceLog.DoesNotExist:
            return None
