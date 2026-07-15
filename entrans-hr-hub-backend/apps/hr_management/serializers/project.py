from rest_framework import serializers
from ..models import Project, UserProject

class ProjectSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ("id", "name", "description", "owner", "owner_name")
        extra_kwargs = {"owner": {"required": False}}

    def get_owner_name(self, obj):
        return obj.owner.name if obj.owner else None


class UserProjectSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProject
        fields = ("id", "user", "project", "user_name", "project_name", "role")

    def get_user_name(self, obj):
        return obj.user.name if obj.user else None

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None
