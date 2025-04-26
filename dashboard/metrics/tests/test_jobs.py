# metrics/tests/test_jobs.py
import pytest
from unittest.mock import patch, Mock, MagicMock
from metrics.jobs import SystemMetricsJob
from metrics.models import Host, SystemMetric
from django.test import TestCase
from django.utils import timezone

class TestSystemMetricsJob(TestCase):
    
    def setUp(self):
        self.job = SystemMetricsJob(api_url="http://test-api.com/metrics")
    
    @patch('metrics.jobs.requests.get')
    def test_run_success(self, mock_get):
        """Test successful execution of the metrics job"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'hostname': 'test-server',
            'ip_address': '192.168.1.100',
            'os_info': 'Ubuntu 20.04',
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cpu': {
                'cores': 4,
                'overall_usage': 0.25  # 25%
            },
            'memory': {
                'total': 8589934592,  # 8GB
                'used': 4294967296,   # 4GB
                'percent_used': 50.0
            },
            'disk': {
                'partitions': [
                    {
                        'mount_point': '/',
                        'total': 107374182400,  # 100GB
                        'used': 32212254720,    # 30GB
                        'percent': 30.0
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # Execute the job
        result = self.job.run()
        
        # Verify job executed successfully
        self.assertTrue(result)
        
        # Verify a host was created
        host = Host.objects.get(hostname='test-server')
        self.assertEqual(host.ip_address, '192.168.1.100')
        self.assertEqual(host.os_info, 'Ubuntu 20.04')
        self.assertEqual(host.cpu_cores, 4)
        
        # Verify a system metric was created
        metric = SystemMetric.objects.filter(host=host).first()
        self.assertIsNotNone(metric)
        self.assertEqual(metric.cpu_usage, 0.25)
        self.assertEqual(metric.memory_total, 8589934592)
        self.assertEqual(metric.memory_used, 4294967296)
        self.assertEqual(metric.memory_percent, 50.0)
        self.assertEqual(metric.disk_total, 107374182400)
        self.assertEqual(metric.disk_used, 32212254720)
        self.assertEqual(metric.disk_percent, 30.0)
    
    @patch('metrics.jobs.requests.get')
    def test_run_request_exception(self, mock_get):
        """Test job handling of a request exception"""
        # Mock the API response to raise an exception
        mock_get.side_effect = Exception("Connection error")
        
        # Execute the job
        result = self.job.run()
        
        # Verify job failed
        self.assertFalse(result)
        
        # Verify no host or metric was created
        self.assertEqual(Host.objects.count(), 0)
        self.assertEqual(SystemMetric.objects.count(), 0)
    
    @patch('metrics.jobs.requests.get')
    def test_process_metrics_multiple_partitions(self, mock_get):
        """Test processing of metrics with multiple disk partitions"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'hostname': 'multi-disk-server',
            'ip_address': '192.168.1.200',
            'os_info': 'Ubuntu 20.04',
            'cpu': {
                'cores': 8,
                'overall_usage': 0.5  # 50%
            },
            'memory': {
                'total': 17179869184,  # 16GB
                'used': 8589934592,    # 8GB
                'percent_used': 50.0
            },
            'disk': {
                'partitions': [
                    {
                        'mount_point': '/',
                        'total': 107374182400,  # 100GB
                        'used': 53687091200,    # 50GB
                    },
                    {
                        'mount_point': '/home',
                        'total': 214748364800,  # 200GB
                        'used': 42949672960,    # 40GB
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # Execute the job
        result = self.job.run()
        
        # Verify job executed successfully
        self.assertTrue(result)
        
        # Verify a host was created
        host = Host.objects.get(hostname='multi-disk-server')
        self.assertEqual(host.cpu_cores, 8)
        
        # Verify a system metric was created
        metric = SystemMetric.objects.filter(host=host).first()
        self.assertIsNotNone(metric)
        
        # Check disk calculations - should sum multiple partitions
        total_disk = 107374182400 + 214748364800  # 300GB
        used_disk = 53687091200 + 42949672960     # 90GB
        expected_percent = (used_disk / total_disk) * 100
        
        self.assertEqual(metric.disk_total, total_disk)
        self.assertEqual(metric.disk_used, used_disk)
        self.assertAlmostEqual(metric.disk_percent, expected_percent)
    
    @patch('metrics.jobs.requests.get')
    def test_process_metrics_update_existing_host(self, mock_get):
        """Test that existing hosts are updated rather than duplicated"""
        # Create a pre-existing host
        Host.objects.create(
            hostname='existing-host',
            ip_address='192.168.1.50',
            os_info='Ubuntu 18.04',
            cpu_cores=2
        )
        
        # Mock the API response with updated host info
        mock_response = Mock()
        mock_response.json.return_value = {
            'hostname': 'existing-host',
            'ip_address': '192.168.1.100',  # Changed
            'os_info': 'Ubuntu 20.04',      # Updated
            'cpu': {
                'cores': 4,                 # Increased
                'overall_usage': 0.3
            },
            'memory': {
                'total': 8589934592,
                'used': 4294967296,
                'percent_used': 50.0
            },
            'disk': {
                'partitions': [
                    {
                        'mount_point': '/',
                        'total': 107374182400,
                        'used': 32212254720,
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        # Execute the job
        result = self.job.run()
        
        # Verify job executed successfully
        self.assertTrue(result)
        
        # Verify there's still only one host
        self.assertEqual(Host.objects.count(), 1)
        
        # Verify the host was updated
        host = Host.objects.get(hostname='existing-host')
        self.assertEqual(host.ip_address, '192.168.1.100')
        self.assertEqual(host.os_info, 'Ubuntu 20.04')
        self.assertEqual(host.cpu_cores, 4)

