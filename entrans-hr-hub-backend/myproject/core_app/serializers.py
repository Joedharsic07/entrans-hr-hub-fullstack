from rest_framework import serializers
from uuid import uuid4
from .models import User, Timesheet, Project, UserProject
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = user.id
        token['type'] = 'access'
        token['jti'] = str(uuid4())
        return token

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField() 
    
    class Meta:
        model = User
        fields = ('id', 'user_id', 'name', 'first_name', 'last_name', 'designation', 'email', 'password', 'role', 'is_active', 'password_changed_at')
        extra_kwargs = {
            'password': {'write_only': True},
            'password_changed_at': {'read_only': True},
        }

    def get_role(self, obj):
        """Determine if user is Admin or Normal User"""
        return "Admin" if (obj.is_staff or obj.is_superuser) else "User"

    def create(self, validated_data):
        """Maintain existing password hashing functionality"""
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'name': {'required': True}
        }

    def validate(self, data):
        # Check passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        
        # Validate password strength
        try:
            validate_password(data['password'])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        # Check unique constraints
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "This email is already registered"})
            
        if User.objects.filter(name=data['name']).exists():
            raise serializers.ValidationError({"name": "This username is already taken"})
            
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            name=validated_data['name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return UserSerializer(obj).data

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        data['user'] = user
        return data

class ProjectSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'owner', 'owner_name')
        extra_kwargs = {'owner': {'required': False}} 
    def get_owner_name(self, obj):
        return obj.owner.name if obj.owner else None

class UserProjectSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProject
        fields = ('id', 'user', 'project', 'user_name', 'project_name','role')
        
    def get_user_name(self, obj):
        return obj.user.name if obj.user else None
        
    def get_project_name(self, obj):
        return obj.project.name if obj.project else None

class TimesheetSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    leave_day_value = serializers.SerializerMethodField()
    task_name = serializers.CharField(required=False, allow_blank=True)
    duration = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Timesheet
        fields = (
            'id', 'user_project', 'date', 'task_name', 'description',
            'duration', 'work_type', 'user_name', 'project_name', 'leave_day_value'
        )

    def get_user_name(self, obj):
        return obj.user_project.user.name if obj.user_project and obj.user_project.user else None

    def get_project_name(self, obj):
        return obj.user_project.project.name if obj.user_project and obj.user_project.project else None

    def get_leave_day_value(self, obj):
        if obj.work_type == 'full_day_leave':
            return 1.0
        elif obj.work_type == 'half_day_leave':
            return 0.5
        return 0.0

    def validate(self, attrs):
        work_type = attrs.get('work_type')

        if work_type not in ['full_day_leave', 'half_day_leave']:
            if not attrs.get('task_name'):
                raise serializers.ValidationError({'task_name': 'This field is required for work entries.'})
            if attrs.get('duration') in (None, ''):
                raise serializers.ValidationError({'duration': 'This field is required for work entries.'})
        return attrs

class UploadExcelSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    years = serializers.CharField(max_length=100)
    file = serializers.FileField()

class UploadTimesheetSerializer(serializers.Serializer):
    timesheet_file = serializers.FileField()
    validation_type = serializers.CharField(max_length=20, required=False, default='standard')

class GenerateTemplateSerializer(serializers.Serializer):
    month = serializers.IntegerField(required=False)
    year = serializers.IntegerField(required=False)

class EmailSerializer(serializers.Serializer):
    recipient_email = serializers.EmailField()
    json_data = serializers.JSONField()