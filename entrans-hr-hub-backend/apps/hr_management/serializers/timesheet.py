from rest_framework import serializers
from ..models import Timesheet

class TimesheetSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    leave_day_value = serializers.SerializerMethodField()
    task_name = serializers.CharField(required=False, allow_blank=True)
    duration = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Timesheet
        fields = (
            "id",
            "user_project",
            "date",
            "task_name",
            "description",
            "duration",
            "work_type",
            "user_name",
            "project_name",
            "leave_day_value",
        )

    def get_user_name(self, obj):
        return (
            obj.user_project.user.name
            if obj.user_project and obj.user_project.user
            else None
        )

    def get_project_name(self, obj):
        return (
            obj.user_project.project.name
            if obj.user_project and obj.user_project.project
            else None
        )

    def get_leave_day_value(self, obj):
        if obj.work_type == "full_day_leave":
            return 1.0
        elif obj.work_type == "half_day_leave":
            return 0.5
        return 0.0

    def validate(self, attrs):
        work_type = attrs.get("work_type")

        if work_type not in ["full_day_leave", "half_day_leave"]:
            if not attrs.get("task_name"):
                raise serializers.ValidationError(
                    {"task_name": "This field is required for work entries."}
                )
            if attrs.get("duration") in (None, ""):
                raise serializers.ValidationError(
                    {"duration": "This field is required for work entries."}
                )
        return attrs


class UploadExcelSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    years = serializers.CharField(max_length=100)
    file = serializers.FileField()


class UploadTimesheetSerializer(serializers.Serializer):
    timesheet_file = serializers.FileField()
    validation_type = serializers.CharField(
        max_length=20, required=False, default="standard"
    )


class GenerateTemplateSerializer(serializers.Serializer):
    month = serializers.IntegerField(required=False)
    year = serializers.IntegerField(required=False)
