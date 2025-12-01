from django.contrib import admin
from .models import Project, GeoData, AdminLog


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'mobile_id',
        'name',
        'geometry_type',
        'created_by',
        'is_active',
        'created_at',
        'updated_at'
    ]
    list_filter = ['geometry_type', 'is_active', 'is_deleted', 'created_at']
    search_fields = ['mobile_id', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('mobile_id', 'name', 'description', 'geometry_type')
        }),
        ('Form Configuration', {
            'fields': ('form_fields',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'is_active', 'is_deleted', 'created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('created_by')


@admin.register(GeoData)
class GeoDataAdmin(admin.ModelAdmin):
    list_display = [
        'mobile_id',
        'project',
        'collected_by',
        'created_at',
        'updated_at',
        'is_deleted'
    ]
    list_filter = ['is_deleted', 'created_at', 'project']
    search_fields = ['mobile_id', 'project__name']
    readonly_fields = ['created_at', 'updated_at', 'synced_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('mobile_id', 'project', 'collected_by')
        }),
        ('Data', {
            'fields': ('form_data', 'points'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'synced_at', 'is_deleted')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('project', 'collected_by')


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'action',
        'resource',
        'resource_id',
        'ip_address',
        'created_at'
    ]
    list_filter = ['action', 'resource', 'created_at']
    search_fields = ['user__username', 'resource', 'resource_id']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User & Action', {
            'fields': ('user', 'action', 'resource', 'resource_id')
        }),
        ('Details', {
            'fields': ('details', 'ip_address'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
    
    # Admin log biasanya read-only
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
