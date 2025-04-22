import pytest
from django.urls import reverse
import requests
from unittest.mock import patch, Mock
from django.contrib.auth.models import User

@pytest.fixture
def mock_metrics_response():
    """Fixture to mock a successful API response"""
    mock_data = {
        'cpu': {'overall_usage': 75},
        'memory': {'percent_used': 60},
        'disk': {'partitions': [
            {'mount_point': '/', 'percent_used': 45}
        ]},
        'processes': [
            {'pid': 1, 'name': 'systemd', 'cpu_percent': 0.5, 'memory_percent': 1.2}
        ]
    }
    return mock_data

@pytest.fixture
def authenticated_client(client):
    """Fixture to create an authenticated test client"""
    # Create a test user
    User.objects.create_user(username='admin', password='password')
    # Log in the client
    client.login(username='admin', password='password')
    return client

@pytest.mark.django_db
class TestViews:
    
    @patch('core.views.requests.get')
    def test_index_view_successful_api(self, mock_get, mock_metrics_response, authenticated_client):
        """Test index view with successful API response"""
        # Configure the mock to return a successful response
        mock_response = Mock()
        mock_response.json.return_value = mock_metrics_response
        mock_get.return_value = mock_response
        
        # Get the index page using authenticated client
        url = reverse('dashboard_index')  # Use the correct URL name from urls.py
        response = authenticated_client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        assert 'metrics' in response.context
        assert response.context['metrics'] == mock_metrics_response
        
    @patch('core.views.requests.get')
    def test_index_view_api_failure(self, mock_get, authenticated_client):
        """Test index view with API failure"""
        # Configure the mock to raise an exception
        mock_get.side_effect = requests.RequestException("API is down")
        
        # Get the index page using authenticated client
        url = reverse('dashboard_index')  # Use the correct URL name from urls.py
        response = authenticated_client.get(url)
        
        # Verify the response - should still render but with default data
        assert response.status_code == 200
        assert 'metrics' in response.context
        assert 'error' in response.context['metrics']
        assert response.context['metrics']['error'] == 'Unable to fetch system metrics'
        assert response.context['metrics']['cpu']['overall_usage'] == 0
        assert response.context['metrics']['memory']['percent_used'] == 0
        
    @patch('core.views.requests.get')
    def test_processes_view_successful_api(self, mock_get, mock_metrics_response, authenticated_client):
        """Test processes view with successful API response"""
        # Configure the mock to return a successful response
        mock_response = Mock()
        mock_response.json.return_value = mock_metrics_response
        mock_get.return_value = mock_response
        
        # Get the processes page using authenticated client
        url = reverse('dashboard_processes')  # Use the correct URL name from urls.py
        response = authenticated_client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        assert 'processes' in response.context
        assert response.context['processes'] == mock_metrics_response['processes']
        
    @patch('core.views.requests.get')
    def test_processes_view_api_failure(self, mock_get, authenticated_client):
        """Test processes view with API failure"""
        # Configure the mock to raise an exception
        mock_get.side_effect = requests.RequestException("API is down")
        
        # Get the processes page using authenticated client
        url = reverse('dashboard_processes')  # Use the correct URL name from urls.py
        response = authenticated_client.get(url)
        
        # Verify the response - should still render but with default data
        assert response.status_code == 200
        assert 'processes' in response.context
        assert response.context['processes'] == []
        
    def test_unauthenticated_access(self, client):
        """Test that unauthenticated access redirects to login page"""
        # Try to access protected pages without authentication
        index_url = reverse('dashboard_index')
        processes_url = reverse('dashboard_processes')
        
        # Get the pages without authentication
        index_response = client.get(index_url)
        processes_response = client.get(processes_url)
        
        # Verify redirects to login page (302 Found)
        assert index_response.status_code == 302
        assert processes_response.status_code == 302
        
        # Verify redirect URLs contain the login path
        assert '/login' in index_response.url
        assert '/login' in processes_response.url