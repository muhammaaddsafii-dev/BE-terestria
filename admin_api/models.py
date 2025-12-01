from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Project(models.Model):
    """Model untuk Project (Read-Only dari mobile app)"""
    GEOMETRY_CHOICES = [
        ('point', 'Point'),
        ('line', 'Line'),
        ('polygon', 'Polygon'),
    ]
    
    mobile_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    geometry_type = models.CharField(max_length=20, choices=GEOMETRY_CHOICES)
    form_fields = models.JSONField(default=list)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_created_projects'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'geoform_projects'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.geometry_type})"


class GeoData(models.Model):
    """Model untuk GeoData (Read-Only dari mobile app)"""
    mobile_id = models.CharField(max_length=100, unique=True, db_index=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='admin_geo_data',
        to_field='mobile_id',
        db_column='project_mobile_id'
    )
    
    form_data = models.JSONField(default=dict)
    points = models.JSONField(default=list)
    
    collected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_collected_geodata'
    )
    
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    synced_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'geoform_geodata'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"GeoData {self.mobile_id} - {self.project.name}"


class AdminLog(models.Model):
    """Log aktivitas admin"""
    ACTION_CHOICES = [
        ('view', 'View'),
        ('export', 'Export'),
        ('filter', 'Filter'),
        ('search', 'Search'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    resource = models.CharField(max_length=100)  # project, geodata, etc
    resource_id = models.CharField(max_length=100, null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_logs'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user} - {self.action} - {self.resource}"
