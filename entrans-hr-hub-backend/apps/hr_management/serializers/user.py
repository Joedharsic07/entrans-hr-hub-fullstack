from rest_framework import serializers
from ..models import User

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "user_id",
            "name",
            "first_name",
            "last_name",
            "designation",
            "email",
            "password",
            "role",
            "is_active",
            "password_changed_at",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "password_changed_at": {"read_only": True},
        }

    def get_role(self, obj):
        return "Admin" if (obj.is_staff or obj.is_superuser) else "User"

    def create(self, validated_data):
        name = validated_data["name"]
        parts = name.strip().split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        user = User.objects.create_user(
            email=validated_data["email"],
            name=name,
            password=validated_data["password"],
        )
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return user
