from hr_management.repositories.notification_repository import NotificationRepository

class NotificationService:
    @staticmethod
    def get_notifications(user):
        return NotificationRepository.get_user_notifications(user)

    @staticmethod
    def mark_as_read(user, notification_id=None):
        if notification_id:
            notification = NotificationRepository.get_user_notification(user, notification_id)
            if not notification:
                raise ValueError("Notification not found")
            notification.is_read = True
            notification.save()
            return notification
        
        NotificationRepository.mark_all_as_read(user)
        return None

    @staticmethod
    def delete_notification(user, notification_id):
        notification = NotificationRepository.get_user_notification(user, notification_id)
        if not notification:
            raise ValueError("Notification not found")
        notification.delete()
