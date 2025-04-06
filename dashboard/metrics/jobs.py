# metrics/jobs.py
import requests
import logging
from datetime import datetime
from django.utils import timezone
from django.conf import settings

from .models import Host, SystemMetric

logger = logging.getLogger(__name__)

class SystemMetricsJob:
    """
    Job that fetches system metrics from a REST API and stores them in the database.
    """
    
    def __init__(self, api_url=None):
        self.api_url = api_url or settings.METRICS_API_URL
    
    def run(self):
        """
        Fetch metrics and store in database.
        """
        try:
            # Get metrics from API
            response = requests.get(self.api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Process and store metrics
            self._process_metrics(data)
            
            logger.info(f"Successfully fetched and stored metrics for host {data.get('hostname')}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch metrics: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error processing metrics: {str(e)}")
            return False
    
    def _process_metrics(self, data):
        """
        Process the metrics data and store in database.
        """
        # Get or create host
        hostname = data.get('hostname')
        host, created = Host.objects.update_or_create(
            hostname=hostname,
            defaults={
                'ip_address': data.get('ip_address'),
                'os_info': data.get('os_info'),
                'cpu_cores': data.get('cpu', {}).get('cores', 0)
            }
        )
        
        # Extract important metrics
        cpu_data = data.get('cpu', {})
        memory_data = data.get('memory', {})
        disk_data = data.get('disk', {})
        
        # Calculate total disk space (sum of all partitions)
        total_disk = 0
        used_disk = 0
        for partition in disk_data.get('partitions', []):
            total_disk += partition.get('total', 0)
            used_disk += partition.get('used', 0)
        
        # Calculate disk usage percentage
        disk_percent = (used_disk / total_disk * 100) if total_disk > 0 else 0
        
        # Parse timestamp or use current time and make timezone-aware
        try:
            timestamp_str = data.get('timestamp')
            if timestamp_str:
                naive_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                # Make timezone-aware
                timestamp = timezone.make_aware(naive_timestamp)
            else:
                timestamp = timezone.now()
        except (ValueError, TypeError):
            timestamp = timezone.now()
        
        # Create metrics record
        SystemMetric.objects.create(
            host=host,
            timestamp=timestamp,
            
            # CPU metrics
            cpu_usage=cpu_data.get('overall_usage', 0) * 100,  # Convert to percentage
            
            # Memory metrics
            memory_total=memory_data.get('total', 0),
            memory_used=memory_data.get('used', 0),
            memory_percent=memory_data.get('percent_used', 0),
            
            # Disk metrics
            disk_total=total_disk,
            disk_used=used_disk,
            disk_percent=disk_percent
        )