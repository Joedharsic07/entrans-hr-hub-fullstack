from rest_framework import serializers
from uuid import uuid4
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from ..models import User
from .user import UserSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_id"] = user.id
        token["type"] = "access"
        token["jti"] = str(uuid4())
        return token

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["name", "email", "password", "confirm_password", "date_of_joining"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "name": {"required": True},
            "date_of_joining": {"required": False},
        }

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})

        try:
            validate_password(data["password"])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError(
                {"email": "This email is already registered"}
            )

        if User.objects.filter(name=data["name"]).exists():
            raise serializers.ValidationError(
                {"name": "This username is already taken"}
            )

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        name = validated_data["name"]
        parts = name.strip().split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        user = User.objects.create_user(
            name=name,
            email=validated_data["email"],
            password=validated_data["password"],
        )
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return UserSerializer(obj).data

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        data["user"] = user
        return data
