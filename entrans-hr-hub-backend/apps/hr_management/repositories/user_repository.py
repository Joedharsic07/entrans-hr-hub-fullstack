from django.contrib.auth import get_user_model
from ..models.user import UserAccessLog
from django.db.models import QuerySet

User = get_user_model()

class UserRepository:
    @staticmethod
    def get_by_email(email: str) -> User | None:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_id(user_id) -> User | None:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def log_access(user, action: str, status: str, ip_address: str, user_agent: str):
        try:
            UserAccessLog.objects.create(
                user=user,
                action=action,
                status=status,
                ip_address=ip_address,
                user_agent=user_agent[:500]
            )
        except Exception:
            pass

    @staticmethod
    def exists_by_email(email: str) -> bool:
        return User.objects.filter(email=email).exists()

    @staticmethod
    def exists_by_name(name: str) -> bool:
        return User.objects.filter(name=name).exists()
