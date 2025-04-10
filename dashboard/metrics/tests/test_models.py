# metrics/tests/test_models.py
import pytest
from django.test import TestCase
from metrics.models import Host, SystemMetric
from datetime import datetime
from django.utils import timezone

class TestHostModel(TestCase):
    def test_host_creation(self):
        """Test Host model creation and string representation"""
        host = Host.objects.create(
            hostname="test-server",
            ip_address="192.168.1.100",
            os_info="Ubuntu 20.04",
            cpu_cores=4
        )
        
        # Verify the object exists
        saved_host = Host.objects.get(id=host.id)
        self.assertEqual(saved_host.hostname, "test-server")
        self.assertEqual(saved_host.ip_address, "192.168.1.100")
        self.assertEqual(saved_host.os_info, "Ubuntu 20.04")
        self.assertEqual(saved_host.cpu_cores, 4)
        
        # Test string representation
        self.assertEqual(str(host), "test-server")

class TestSystemMetricModel(TestCase):
    def setUp(self):
        # Create a test host
        self.host = Host.objects.create(
            hostname="test-server",
            ip_address="192.168.1.100",
            os_info="Ubuntu 20.04",
            cpu_cores=4
        )
    
    def test_system_metric_creation(self):
        """Test SystemMetric model creation and string representation"""
        timestamp = timezone.now()
        
        metric = SystemMetric.objects.create(
            host=self.host,
            timestamp=timestamp,
            cpu_usage=25.5,
            memory_total=8589934592,  # 8GB in bytes
            memory_used=4294967296,   # 4GB in bytes
            memory_percent=50.0,
            disk_total=107374182400,  # 100GB in bytes
            disk_used=32212254720,    # 30GB in bytes
            disk_percent=30.0
        )
        
        # Verify the object exists
        saved_metric = SystemMetric.objects.get(id=metric.id)
        self.assertEqual(saved_metric.host, self.host)
        self.assertEqual(saved_metric.timestamp, timestamp)
        self.assertEqual(saved_metric.cpu_usage, 25.5)
        self.assertEqual(saved_metric.memory_total, 8589934592)
        self.assertEqual(saved_metric.memory_used, 4294967296)
        self.assertEqual(saved_metric.memory_percent, 50.0)
        self.assertEqual(saved_metric.disk_total, 107374182400)
        self.assertEqual(saved_metric.disk_used, 32212254720)
        self.assertEqual(saved_metric.disk_percent, 30.0)
        
        # Test string representation
        expected_str = f"{self.host.hostname} - {timestamp}"
        self.assertEqual(str(metric), expected_str)
    
    def test_ordering(self):
        """Test that SystemMetric records are ordered by timestamp in descending order"""
        # Create metrics with different timestamps
        timestamp1 = timezone.make_aware(datetime(2023, 1, 1, 12, 0, 0))
        timestamp2 = timezone.make_aware(datetime(2023, 1, 1, 13, 0, 0))
        timestamp3 = timezone.make_aware(datetime(2023, 1, 1, 14, 0, 0))
        
        metric1 = SystemMetric.objects.create(
            host=self.host, timestamp=timestamp1, 
            cpu_usage=25.0, memory_total=8000000000, memory_used=4000000000, memory_percent=50.0,
            disk_total=100000000000, disk_used=30000000000, disk_percent=30.0
        )
        
        metric2 = SystemMetric.objects.create(
            host=self.host, timestamp=timestamp2, 
            cpu_usage=30.0, memory_total=8000000000, memory_used=4800000000, memory_percent=60.0,
            disk_total=100000000000, disk_used=35000000000, disk_percent=35.0
        )
        
        metric3 = SystemMetric.objects.create(
            host=self.host, timestamp=timestamp3, 
            cpu_usage=35.0, memory_total=8000000000, memory_used=5600000000, memory_percent=70.0,
            disk_total=100000000000, disk_used=40000000000, disk_percent=40.0
        )
        
        # Query all metrics and verify ordering (newest first)
        metrics = SystemMetric.objects.all()
        self.assertEqual(metrics[0].id, metric3.id)
        self.assertEqual(metrics[1].id, metric2.id)
