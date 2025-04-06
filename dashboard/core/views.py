import requests
from django.shortcuts import render
from django.conf import settings

def index(request):
    """
    Main dashboard view that fetches system metrics from the API
    """
    try:
        # Fetch metrics from the API
        response = requests.get(settings.METRICS_API_URL)
        metrics_data = response.json()
    except requests.RequestException:
        # Handle API request failure
        metrics_data = {
            'error': 'Unable to fetch system metrics',
            'cpu': {'overall_usage': 0},
            'memory': {'percent_used': 0},
            'disk': {'partitions': []},
            'processes': []
        }

    context = {
        'metrics': metrics_data
    }
    return render(request, 'dashboard/index.html', context)

def processes(request):
    """
    Processes view that can be used for a separate processes page
    """
    try:
        # Fetch metrics from the API
        response = requests.get(settings.METRICS_API_URL)
        metrics_data = response.json()
    except requests.RequestException:
        metrics_data = {
            'processes': []
        }

    context = {
        'processes': metrics_data.get('processes', [])
    }
    return render(request, 'dashboard/processes.html', context)