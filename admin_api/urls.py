from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, GeoDataViewSet, AdminLogViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'geodata', GeoDataViewSet, basename='geodata')
router.register(r'logs', AdminLogViewSet, basename='log')

urlpatterns = [
    path('', include(router.urls)),
]
