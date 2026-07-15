from hr_management.models.leave import LeaveRequest, LeaveBalance, LeaveType
from django.db.models import QuerySet

class LeaveRepository:
    @staticmethod
    def get_request_by_id(leave_id) -> LeaveRequest | None:
        try:
            return LeaveRequest.objects.get(id=leave_id)
        except LeaveRequest.DoesNotExist:
            return None

    @staticmethod
    def get_all_requests() -> QuerySet:
        return LeaveRequest.objects.all().order_by('-applied_on')

    @staticmethod
    def get_user_requests(user) -> QuerySet:
        return LeaveRequest.objects.filter(employee=user).order_by('-applied_on')

    @staticmethod
    def get_balance(user, leave_type) -> LeaveBalance:
        balance, _ = LeaveBalance.objects.get_or_create(
            employee=user, 
            leave_type=leave_type, 
            defaults={'total_days': 12.0}
        )
        return balance

    @staticmethod
    def get_user_balances(user) -> QuerySet:
        return LeaveBalance.objects.filter(employee=user)
