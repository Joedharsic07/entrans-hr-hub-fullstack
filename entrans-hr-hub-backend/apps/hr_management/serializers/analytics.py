from rest_framework import serializers
from ..models import PPTGenerationLog

class PPTGenerationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPTGenerationLog
        fields = ["id", "employee_name", "years_of_service", "created_at", "created_by"]
        read_only_fields = ["created_at", "created_by"]
