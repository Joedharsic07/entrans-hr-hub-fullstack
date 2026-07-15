from rest_framework import generics, permissions, status
from rest_framework.response import Response
from hr_management.serializers.notification import NotificationSerializer
from hr_management.services.notification_service import NotificationService

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationService.get_notifications(self.request.user)

class NotificationReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationService.get_notifications(self.request.user)

    def post(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            try:
                notification = NotificationService.mark_as_read(request.user, kwargs['pk'])
                return Response(self.get_serializer(notification).data)
            except ValueError as ve:
                return Response({"error": str(ve)}, status=status.HTTP_404_NOT_FOUND)
        
        NotificationService.mark_as_read(request.user)
        return Response({"status": "All notifications marked as read."})

class NotificationDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationService.get_notifications(self.request.user)
