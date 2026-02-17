"""
Serializers for Django REST Framework
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Users, Accounts, Projects, Issues, IssueComments,
    Companies, DataBases, Services, ProjectTeams, ClientTeams
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Users model"""
    email = serializers.EmailField(source='auth_user.email', read_only=True)
    username = serializers.CharField(source='auth_user.username', read_only=True)
    
    class Meta:
        model = Users
        fields = [
            'id', 'email', 'username', 'name', 'phone', 'role',
            'external_id', 'created_at', 'updated_at', 'owner_id',
            'permitted_accounts'
        ]
        read_only_fields = ['id', 'external_id', 'created_at', 'updated_at']


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for Accounts model"""
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = Accounts
        fields = [
            'id', 'name', 'slug', 'content', 'date_create', 'date_expired',
            'user', 'user_name'
        ]
        read_only_fields = ['id', 'date_create']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Projects model"""
    manager_name = serializers.CharField(source='manager.name', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    
    class Meta:
        model = Projects
        fields = [
            'id', 'name', 'description', 'created_at', 'updated_at',
            'manager', 'manager_name', 'owner', 'owner_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class IssueCommentSerializer(serializers.ModelSerializer):
    """Serializer for Issue Comments"""
    author_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = IssueComments
        fields = [
            'id', 'issue', 'user', 'author_name', 'comment',
            'date_create'
        ]
        read_only_fields = ['id', 'date_create']


class IssueSerializer(serializers.ModelSerializer):
    """Serializer for Issues model"""
    supervisor_name = serializers.CharField(source='supervisor.name', read_only=True)
    users_name = serializers.CharField(source='users.name', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    companies_name = serializers.CharField(source='companies.name', read_only=True)
    databases_path = serializers.CharField(source='databases.path', read_only=True)
    services_name = serializers.CharField(source='services.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    sprint_name = serializers.CharField(source='sprint.name', read_only=True)
    
    class Meta:
        model = Issues
        fields = [
            'id', 'name', 'content', 'status', 'priority',
            'supervisor', 'supervisor_name',
            'users', 'users_name',
            'owner', 'owner_name',
            'companies', 'companies_name',
            'databases', 'databases_path',
            'services', 'services_name',
            'parent', 'parent_name',
            'sprint', 'sprint_name',
            'date_create', 'date_check', 'date_end_plan', 'date_start_plan',
            'applicant_content_type', 'applicant_object_id',
            'comment', 'deadline',
            'time_dead_line', 'time_check',
            'sla_reac', 'sla_exec', 'sla_check', 'sla_deadline',
        ]
        read_only_fields = ['id', 'date_create']
    
    def to_representation(self, instance):
        """Добавляем комментарии в представление"""
        representation = super().to_representation(instance)
        # Получаем комментарии для этой задачи
        comments = IssueComments.objects.filter(issue=instance)
        representation['comments'] = IssueCommentSerializer(comments, many=True).data
        return representation


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Companies model"""
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    
    class Meta:
        model = Companies
        fields = [
            'id', 'name', 'tax_code', 'code', 'content', 'owner', 'owner_name',
            'applicant', 'date_create', 'date_expired'
        ]
        read_only_fields = ['id', 'date_create']


class DatabaseSerializer(serializers.ModelSerializer):
    """Serializer for DataBases model"""
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    
    class Meta:
        model = DataBases
        fields = [
            'id', 'path', 'server', 'content', 'comment',
            'owner', 'owner_name', 'date_create'
        ]
        read_only_fields = ['id', 'date_create']


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Services model"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Services
        fields = [
            'id', 'price', 'time_check', 'time_dead_line', 'content',
            'to_do_task', 'create_sd_issue', 'tags', 'company', 'company_name',
            'user', 'applicant', 'supervisor', 'date_create', 'date_expired'
        ]
        read_only_fields = ['id', 'date_create']


class ProjectTeamSerializer(serializers.ModelSerializer):
    """Serializer for Project Teams"""
    user_name = serializers.CharField(source='user.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = ProjectTeams
        fields = [
            'id', 'project', 'project_name', 'user', 'user_name', 'role'
        ]
        read_only_fields = ['id']


class ClientTeamSerializer(serializers.ModelSerializer):
    """Serializer for Client Teams"""
    user_name = serializers.CharField(source='user.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = ClientTeams
        fields = [
            'id', 'company', 'company_name', 'user', 'user_name', 'role'
        ]
        read_only_fields = ['id']

