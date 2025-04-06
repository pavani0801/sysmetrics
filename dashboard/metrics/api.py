# metrics/api.py
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Max, Min
from django.utils import timezone
from datetime import timedelta

from .models import Host, SystemMetric

class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ['id', 'hostname', 'ip_address', 'os_info', 'cpu_cores']

class SystemMetricSerializer(serializers.ModelSerializer):
    hostname = serializers.CharField(source='host.hostname', read_only=True)
    
    class Meta:
        model = SystemMetric
        fields = [
            'id', 'hostname', 'timestamp', 
            'cpu_usage', 
            'memory_total', 'memory_used', 'memory_percent',
            'disk_total', 'disk_used', 'disk_percent'
        ]

class HostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    
    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        host = self.get_object()
        
        # Get query parameters for filtering
        days = request.query_params.get('days', 1)
        try:
            days = int(days)
        except ValueError:
            days = 1
            
        time_range = timezone.now() - timedelta(days=days)
        
        # Get metrics for this host
        metrics = SystemMetric.objects.filter(
            host=host,
            timestamp__gte=time_range
        )
        
        serializer = SystemMetricSerializer(metrics, many=True)
        return Response(serializer.data)

class SystemMetricViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemMetric.objects.all()
    serializer_class = SystemMetricSerializer
    
    def get_queryset(self):
        queryset = SystemMetric.objects.all()
        
        # Filter by hostname if provided
        hostname = self.request.query_params.get('hostname')
        if hostname:
            queryset = queryset.filter(host__hostname=hostname)
        
        # Filter by time range
        days = self.request.query_params.get('days', 1)
        try:
            days = int(days)
        except ValueError:
            days = 1
            
        time_range = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(timestamp__gte=time_range)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get aggregated metrics summary for visualization
        """
        # Get query parameters
        hostname = request.query_params.get('hostname')
        days = request.query_params.get('days', 1)
        
        try:
            days = int(days)
        except ValueError:
            days = 1
            
        time_range = timezone.now() - timedelta(days=days)
        
        # Base queryset
        queryset = SystemMetric.objects.filter(timestamp__gte=time_range)
        
        # Filter by hostname if provided
        if hostname:
            queryset = queryset.filter(host__hostname=hostname)
        
        # Get hourly averages for time series visualization
        hourly_data = []
        
       
        metrics = queryset.order_by('timestamp')
        
        # Group by hour
        metrics_by_hour = {}
        for metric in metrics:
            hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
            if hour_key not in metrics_by_hour:
                metrics_by_hour[hour_key] = []
            metrics_by_hour[hour_key].append(metric)
        
        # Calculate averages for each hour
        for hour, hour_metrics in metrics_by_hour.items():
            avg_cpu = sum(m.cpu_usage for m in hour_metrics) / len(hour_metrics)
            avg_memory = sum(m.memory_percent for m in hour_metrics) / len(hour_metrics)
            avg_disk = sum(m.disk_percent for m in hour_metrics) / len(hour_metrics)
            
            hourly_data.append({
                'timestamp': hour,
                'cpu_usage': avg_cpu,
                'memory_percent': avg_memory,
                'disk_percent': avg_disk
            })
        
        # Get overall stats
        if queryset.exists():
            overall_stats = {
                'cpu_usage': {
                    'avg': queryset.aggregate(Avg('cpu_usage'))['cpu_usage__avg'],
                    'max': queryset.aggregate(Max('cpu_usage'))['cpu_usage__max'],
                    'min': queryset.aggregate(Min('cpu_usage'))['cpu_usage__min'],
                },
                'memory_percent': {
                    'avg': queryset.aggregate(Avg('memory_percent'))['memory_percent__avg'],
                    'max': queryset.aggregate(Max('memory_percent'))['memory_percent__max'],
                    'min': queryset.aggregate(Min('memory_percent'))['memory_percent__min'],
                },
                'disk_percent': {
                    'avg': queryset.aggregate(Avg('disk_percent'))['disk_percent__avg'],
                    'max': queryset.aggregate(Max('disk_percent'))['disk_percent__max'],
                    'min': queryset.aggregate(Min('disk_percent'))['disk_percent__min'],
                }
            }
        else:
            overall_stats = {}
        
        return Response({
            'time_series': hourly_data,
            'overall_stats': overall_stats
        })