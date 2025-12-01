from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, GeoData, AdminLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer untuk list projects"""
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    geodata_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id',
            'mobile_id',
            'name',
            'description',
            'geometry_type',
            'created_by_username',
            'created_at',
            'updated_at',
            'is_active',
            'geodata_count',
        ]
    
    def get_geodata_count(self, obj):
        return obj.admin_geo_data.filter(is_deleted=False).count()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer untuk detail project"""
    created_by = UserSerializer(read_only=True)
    form_fields = serializers.JSONField()
    
    class Meta:
        model = Project
        fields = '__all__'


class GeoDataListSerializer(serializers.ModelSerializer):
    """Serializer untuk list geodata"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    collected_by_username = serializers.CharField(
        source='collected_by.username',
        read_only=True
    )
    
    class Meta:
        model = GeoData
        fields = [
            'id',
            'mobile_id',
            'project',
            'project_name',
            'collected_by_username',
            'created_at',
            'updated_at',
        ]


class GeoDataDetailSerializer(serializers.ModelSerializer):
    """Serializer untuk detail geodata"""
    project = ProjectListSerializer(read_only=True)
    collected_by = UserSerializer(read_only=True)
    
    class Meta:
        model = GeoData
        fields = '__all__'


class AdminLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AdminLog
        fields = '__all__'
