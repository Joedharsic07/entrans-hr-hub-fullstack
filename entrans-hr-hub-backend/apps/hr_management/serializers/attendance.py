from rest_framework import serializers
from ..models import AttendanceLog

class AttendanceLogSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)

    class Meta:
        model = AttendanceLog
        fields = '__all__'
