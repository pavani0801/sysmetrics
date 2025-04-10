# metrics/tests/test_api.py
import pytest
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
import json

from metrics.models import Host, SystemMetric
from metrics.api import HostSerializer, SystemMetricSerializer

class TestHostAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test hosts
        self.host1 = Host.objects.create(
            hostname="server1",
            ip_address="192.168.1.101",
            os_info="Ubuntu 20.04",
            cpu_cores=4
        )
        
        self.host2 = Host.objects.create(
            hostname="server2",
            ip_address="192.168.1.102",
            os_info="CentOS 8",
            cpu_cores=8
        )
        
        # Create metrics for host1
        now = timezone.now()
        for i in range(5):
            timestamp = now - timedelta(hours=i)
            SystemMetric.objects.create(
                host=self.host1,
                timestamp=timestamp,
                cpu_usage=25.0 + i * 5,
                memory_total=8589934592,
                memory_used=4294967296 + i * 536870912,
                memory_percent=50.0 + i * 5,
                disk_total=107374182400,
                disk_used=32212254720 + i * 2147483648,
                disk_percent=30.0 + i * 2
            )
    
    def test_list_hosts(self):
        """Test listing all hosts"""
        url = reverse('host-list')  # Assuming your URL pattern is named this way
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Check host data
        hosts = response.data
        self.assertEqual(hosts[0]['hostname'], self.host1.hostname)
        self.assertEqual(hosts[1]['hostname'], self.host2.hostname)
    
    def test_retrieve_host(self):
        """Test retrieving a single host"""
        url = reverse('host-detail', kwargs={'pk': self.host1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['hostname'], self.host1.hostname)
        self.assertEqual(response.data['ip_address'], self.host1.ip_address)
        self.assertEqual(response.data['os_info'], self.host1.os_info)
        self.assertEqual(response.data['cpu_cores'], self.host1.cpu_cores)
    
    def test_host_metrics_action(self):
        """Test the metrics action for a host"""
        url = reverse('host-metrics', kwargs={'pk': self.host1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return all metrics for the host (default 1 day)
        self.assertEqual(len(response.data), 5)
        
        # Check first metric
        first_metric = response.data[0]
        self.assertEqual(first_metric['hostname'], self.host1.hostname)
        
        # Test with days parameter
        url = f"{url}?days=2"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)  # All metrics are within 2 days
        
        # Test with invalid days parameter
        url = f"{url}?days=invalid"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)  # Should default to 1 day

class TestSystemMetricAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test hosts
        self.host1 = Host.objects.create(
            hostname="server1",
            ip_address="192.168.1.101",
            os_info="Ubuntu 20.04",
            cpu_cores=4
        )
        
        self.host2 = Host.objects.create(
            hostname="server2",
            ip_address="192.168.1.102",
            os_info="CentOS 8",
            cpu_cores=8
        )
        
        # Create metrics for both hosts
        now = timezone.now()
        
        # Create metrics for host1
        for i in range(5):
            timestamp = now - timedelta(hours=i)
            SystemMetric.objects.create(
                host=self.host1,
                timestamp=timestamp,
                cpu_usage=25.0 + i * 5,
                memory_total=8589934592,
                memory_used=4294967296 + i * 536870912,
                memory_percent=50.0 + i * 5,
                disk_total=107374182400,
                disk_used=32212254720 + i * 2147483648,
                disk_percent=30.0 + i * 2
            )
        
        # Create metrics for host2
        for i in range(3):
            timestamp = now - timedelta(hours=i)
            SystemMetric.objects.create(
                host=self.host2,
                timestamp=timestamp,
                cpu_usage=35.0 + i * 5,
                memory_total=17179869184,
                memory_used=8589934592 + i * 1073741824,
                memory_percent=50.0 + i * 5,
                disk_total=214748364800,
                disk_used=64424509440 + i * 10737418240,
                disk_percent=30.0 + i * 5
            )
    
    def test_list_metrics(self):
        """Test listing all metrics"""
        url = reverse('systemmetric-list')  # Assuming your URL pattern is named this way
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8)  # 5 + 3 metrics total
    
    def test_filter_by_hostname(self):
        """Test filtering metrics by hostname"""
        url = reverse('systemmetric-list')
        url = f"{url}?hostname=server1"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)  # Only server1 metrics
        
        # Check hostname in response
        for metric in response.data:
            self.assertEqual(metric['hostname'], 'server1')
    
    def test_filter_by_days(self):
        """Test filtering metrics by time range"""
        # Add an older metric outside the default range
        old_metric = SystemMetric.objects.create(
            host=self.host1,
            timestamp=timezone.now() - timedelta(days=2),
            cpu_usage=10.0,
            memory_total=8589934592,
            memory_used=2147483648,
            memory_percent=25.0,
            disk_total=107374182400,
            disk_used=21474836480,
            disk_percent=20.0
        )
        
        # Default range (1 day)
        url = reverse('systemmetric-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8)  # Only the metrics within 1 day
        
        # Extend range to include older metric
        url = f"{url}?days=3"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 9)  # Including the older metric
    
    def test_summary_action(self):
        """Test the summary action"""
        url = reverse('systemmetric-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('time_series', response.data)
        self.assertIn('overall_stats', response.data)
        
        # Check overall stats
        stats = response.data['overall_stats']
        self.assertIn('cpu_usage', stats)
        self.assertIn('memory_percent', stats)
        self.assertIn('disk_percent', stats)
        
        # Test with hostname filter
        url = f"{url}?hostname=server1"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Time series data should be grouped by hour
        time_series = response.data['time_series']
        # Number of hours depends on how the test data was created
        self.assertTrue(len(time_series) <= 5)  # At most 5 hours
        
        # Check structure of time series data
        for entry in time_series:
            self.assertIn('timestamp', entry)
            self.assertIn('cpu_usage', entry)
            self.assertIn('memory_percent', entry)
            self.assertIn('disk_percent', entry)

class TestSerializers(TestCase):
    def setUp(self):
        self.host = Host.objects.create(
            hostname="test-server",
            ip_address="192.168.1.100",
            os_info="Ubuntu 20.04",
            cpu_cores=4
        )
        
        self.metric = SystemMetric.objects.create(
            host=self.host,
            timestamp=timezone.now(),
            cpu_usage=25.0,
            memory_total=8589934592,
            memory_used=4294967296,
            memory_percent=50.0,
            disk_total=107374182400,
            disk_used=32212254720,
            disk_percent=30.0
        )
    
    def test_host_serializer(self):
        """Test the HostSerializer"""
        serializer = HostSerializer(self.host)
        data = serializer.data
        
        self.assertEqual(data['hostname'], self.host.hostname)
        self.assertEqual(data['ip_address'], self.host.ip_address)
        self.assertEqual(data['os_info'], self.host.os_info)
        self.assertEqual(data['cpu_cores'], self.host.cpu_cores)
    
    def test_system_metric_serializer(self):
        """Test the SystemMetricSerializer"""
        serializer = SystemMetricSerializer(self.metric)
        data = serializer.data
        
        self.assertEqual(data['hostname'], self.host.hostname)
        self.assertEqual(data['cpu_usage'], self.metric.cpu_usage)
        self.assertEqual(data['memory_total'], self.metric.memory_total)
        self.assertEqual(data['memory_used'], self.metric.memory_used)
        self.assertEqual(data['memory_percent'], self.metric.memory_percent)
        self.assertEqual(data['disk_total'], self.metric.disk_total)
        self.assertEqual(data['disk_used'], self.metric.disk_used)
        self.assertEqual(data['disk_percent'], self.metric.disk_percent)