from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Task
from apps.users.serializers import UserSerializer



class TaskSerializer(serializers.ModelSerializer):
    """
    Task serializer with all fields
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = (
            'id', 'user', 'title', 'description', 'status', 
            'result', 'celery_task_id',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'user', 'status', 'result', 
            'celery_task_id', 'created_at', 'updated_at'
        )


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating tasks
    """
    class Meta:
        model = Task
        fields = ('title', 'description')
    
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value


class TaskListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing tasks
    """
    class Meta:
        model = Task
        fields = (
            'id', 'title', 'status', 
            'created_at', 'updated_at'
        )