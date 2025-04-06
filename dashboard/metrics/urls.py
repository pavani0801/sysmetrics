# metrics/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import HostViewSet, SystemMetricViewSet

router = DefaultRouter()
router.register(r'hosts', HostViewSet)
router.register(r'metrics', SystemMetricViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

