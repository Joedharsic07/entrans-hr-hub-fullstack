from hr_management.models.notification import Notification
from django.db.models import QuerySet

class NotificationRepository:
    @staticmethod
    def get_by_id(notification_id) -> Notification | None:
        try:
            return Notification.objects.get(id=notification_id)
        except Notification.DoesNotExist:
            return None

    @staticmethod
    def get_user_notifications(user) -> QuerySet:
        return Notification.objects.filter(user=user).order_by('-created_at')

    @staticmethod
    def get_user_notification(user, notification_id) -> Notification | None:
        try:
            return Notification.objects.get(user=user, id=notification_id)
        except Notification.DoesNotExist:
            return None

    @staticmethod
    def mark_all_as_read(user):
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
