from hr_management.repositories.leave_repository import LeaveRepository
from hr_management.models.leave import LeaveType

class LeaveService:
    @staticmethod
    def get_leave_requests(user):
        if user.is_staff:
            return LeaveRepository.get_all_requests()
        return LeaveRepository.get_user_requests(user)

    @staticmethod
    def approve_leave_request(instance, user):
        if not user.is_staff:
            raise PermissionError("Only admins can change leave status.")
        
        days = (instance.end_date - instance.start_date).days + 1
        balance = LeaveRepository.get_balance(instance.employee, instance.leave_type)
        
        if balance.remaining_days >= days:
            balance.used_days += days
            balance.save()
        else:
            raise ValueError("Insufficient leave balance")

    @staticmethod
    def ensure_balances_exist(user):
        for l_type in LeaveType.choices:
            LeaveRepository.get_balance(user, l_type[0])
        return LeaveRepository.get_user_balances(user)
