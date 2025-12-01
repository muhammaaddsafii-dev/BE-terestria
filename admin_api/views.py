from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import Project, GeoData, AdminLog
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    GeoDataListSerializer,
    GeoDataDetailSerializer,
    AdminLogSerializer,
)
from .permissions import IsAdminUser


def get_client_ip(request):
    """Get client IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_admin_action(request, action, resource, resource_id=None, details=None):
    """Helper untuk log aktivitas admin"""
    AdminLog.objects.create(
        user=request.user,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details,
        ip_address=get_client_ip(request)
    )


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet untuk admin mengelola Projects (Read-Only)
    
    Endpoints:
    - GET /api/projects/ - List semua projects
    - GET /api/projects/{id}/ - Detail project
    - GET /api/projects/statistics/ - Statistik projects
    - GET /api/projects/{id}/geodata/ - GeoData dari project tertentu
    """
    queryset = Project.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['geometry_type', 'is_active', 'created_by']
    search_fields = ['name', 'description', 'mobile_id']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectListSerializer
    
    def list(self, request, *args, **kwargs):
        log_admin_action(request, 'view', 'project')
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        log_admin_action(request, 'view', 'project', instance.mobile_id)
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistik projects"""
        queryset = self.filter_queryset(self.get_queryset())
        
        total = queryset.count()
        by_geometry = queryset.values('geometry_type').annotate(
            count=Count('id')
        )
        by_active = queryset.values('is_active').annotate(
            count=Count('id')
        )
        
        log_admin_action(request, 'view', 'project_statistics')
        
        return Response({
            'total_projects': total,
            'by_geometry_type': list(by_geometry),
            'by_active_status': list(by_active),
        })
    
    @action(detail=True, methods=['get'])
    def geodata(self, request, pk=None):
        """Get all geodata untuk project tertentu"""
        project = self.get_object()
        geodata = GeoData.objects.filter(
            project=project,
            is_deleted=False
        ).select_related('collected_by')
        
        serializer = GeoDataListSerializer(geodata, many=True)
        
        log_admin_action(
            request,
            'view',
            'project_geodata',
            project.mobile_id,
            {'geodata_count': geodata.count()}
        )
        
        return Response({
            'project': ProjectListSerializer(project).data,
            'geodata': serializer.data,
            'total': geodata.count(),
        })


class GeoDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet untuk admin mengelola GeoData (Read-Only)
    
    Endpoints:
    - GET /api/geodata/ - List semua geodata
    - GET /api/geodata/{id}/ - Detail geodata
    - GET /api/geodata/statistics/ - Statistik geodata
    - GET /api/geodata/export/ - Export data (CSV/JSON)
    """
    queryset = GeoData.objects.filter(is_deleted=False).select_related(
        'project', 'collected_by'
    )
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'collected_by', 'created_at']
    search_fields = ['mobile_id', 'project__name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GeoDataDetailSerializer
        return GeoDataListSerializer
    
    def list(self, request, *args, **kwargs):
        log_admin_action(request, 'view', 'geodata')
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        log_admin_action(request, 'view', 'geodata', instance.mobile_id)
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistik geodata"""
        queryset = self.filter_queryset(self.get_queryset())
        
        total = queryset.count()
        by_project = queryset.values('project__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        log_admin_action(request, 'view', 'geodata_statistics')
        
        return Response({
            'total_geodata': total,
            'top_10_projects': list(by_project),
        })
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export geodata (placeholder - implement sesuai kebutuhan)"""
        # TODO: Implement CSV/Excel export
        log_admin_action(request, 'export', 'geodata')
        
        return Response({
            'message': 'Export feature - coming soon',
            'format': request.query_params.get('format', 'csv'),
        })


class AdminLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet untuk melihat log aktivitas admin
    
    Endpoints:
    - GET /api/logs/ - List semua logs
    - GET /api/logs/{id}/ - Detail log
    """
    queryset = AdminLog.objects.all()
    serializer_class = AdminLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'action', 'resource']
    ordering = ['-created_at']
