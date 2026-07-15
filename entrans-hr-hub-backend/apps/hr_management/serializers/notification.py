from rest_framework import serializers
from ..models import Notification, ActivityLog

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'

class EmailSerializer(serializers.Serializer):
    recipient_email = serializers.EmailField()
    json_data = serializers.JSONField()
