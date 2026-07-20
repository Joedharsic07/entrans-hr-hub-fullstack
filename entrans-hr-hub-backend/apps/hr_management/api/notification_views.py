from rest_framework import generics, permissions, status
from rest_framework.response import Response
from hr_management.serializers.notification import NotificationSerializer
from hr_management.services.notification_service import NotificationService
import time
import json
import queue
from django.http import StreamingHttpResponse, JsonResponse
from django.views import View
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework_simplejwt.authentication import JWTAuthentication
from hr_management.models.notification import Notification

# Global registry of active SSE connections
# Maps user_id to a list of queue.Queue
active_streams = {}

@receiver(post_save, sender=Notification)
@receiver(post_delete, sender=Notification)
def notification_changed(sender, instance, **kwargs):
    user_id = instance.user_id
    if user_id in active_streams:
        for q in active_streams[user_id]:
            q.put('update')


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

class NotificationStreamView(View):
    def get(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({"error": "Token required"}, status=401)
            
        token = auth_header.split(' ')[1]
        
        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
        except Exception:
            return JsonResponse({"error": "Invalid token"}, status=401)
            
        def event_stream():
            user_id = user.id
            q = queue.Queue()
            
            if user_id not in active_streams:
                active_streams[user_id] = []
            active_streams[user_id].append(q)
            
            try:
                # Yield initial state
                current_notifications = NotificationService.get_notifications(user)
                data = NotificationSerializer(current_notifications, many=True).data
                yield f"data: {json.dumps(data)}\n\n"
                
                while True:
                    try:
                        # Block until an event occurs or timeout for heartbeat (every 2s)
                        _ = q.get(timeout=2)
                        
                        # When an update happens, fetch fresh data
                        current_notifications = NotificationService.get_notifications(user)
                        data = NotificationSerializer(current_notifications, many=True).data
                        yield f"data: {json.dumps(data)}\n\n"
                        
                    except queue.Empty:
                        # Timeout reached, send heartbeat
                        yield ": heartbeat\n\n"
            finally:
                if user_id in active_streams:
                    if q in active_streams[user_id]:
                        active_streams[user_id].remove(q)
                    if not active_streams[user_id]:
                        del active_streams[user_id]
                
        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
