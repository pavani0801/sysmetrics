# Metrics Collection Agent

A lightweight agent for collecting system metrics on Linux hosts and exposing them via a RESTful API.

## Overview

This agent collects detailed system metrics including:
- CPU usage and statistics
- Memory and swap usage
- Disk usage, partitions, and I/O statistics
- Process information (PID, name, CPU/memory usage, etc.)
- The agent code is stored under agent folder

Data is collected using Python's `psutil` library, which provides a cross-platform way to retrieve the information.

## Requirements

- Python 3.8+
- Linux environment 
- Network connectivity for API access

## Installation

1. Clone or download the project code
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the agent:

```bash
python agent/main.py

In browser open url http://127.0.0.1:8000/metrics

```

```json
Sample Agent Response
{
  "timestamp": "2025-03-18 16:35:24",
  "hostname": "Host1",
  "ip_address": "127.0.1.1",
  "os_info": "Linux 5",
  "cpu": {
    "percent_usage_per_core": [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    "overall_usage": 0.0909090909090909,
    "user": 0.2,
    "system": 0.3,
    "idle": 99.3,
    "cores": 22,
    "physical_cores": 11
  },
  "memory": {
    "total": 33369800704,
    "available": 30727110656,
    "used": 2189152256,
    "free": 30334898176,
    "percent_used": 7.9,
    "swap_total": 8589934592,
    "swap_used": 0,
    "swap_percent": 0
  },
  "disk": {
    "partitions": [
      {
        "device": "/dev/sdd",
        "mountpoint": "/mnt/sda1",
        "fstype": "ext4",
        "total": 1081101176832,
        "used": 18620567552,
        "free": 1007488253952,
        "percent_used": 1.8
      }
    ]
  }
}
```

# System Metrics Collector

A Django application that collects and stores system metrics (CPU, memory, and disk usage) from hosts.

## Features

- **Automated Collection**: Scheduled job fetches system metrics every 1 minutes
- **Storage**: Stores the  metrics for visualization
- **RESTful API**: Access to historical metric data
- **Time Series**: Track system performance over time

## How It Works

The application consists of:

1. **Scheduler**: Background job that runs on a configurable interval
2. **API Client**: Fetches metrics from  system metrics API endpoint
3. **Database Storage**: Stores key performance metrics
4. **REST API**: Provides access to the collected data



## API Endpoints

- `/api/hosts/` - List all monitored hosts
- `/api/metrics/` - Access raw metrics data


## Sample API Response

```json
[
    {
        "id": 21,
        "hostname": "linux",
        "timestamp": "2025-04-06T18:03:14Z",
        "cpu_usage": 10.18181818181817,
        "memory_total": 33369800704,
        "memory_used": 1814437888,
        "memory_percent": 6.6,
        "disk_total": 2162202353664,
        "disk_used": 23720402944,
        "disk_percent": 1.0970482436023694
    },
    {
        "id": 20,
        "hostname": "linux",
        "timestamp": "2025-04-06T18:02:14Z",
        "cpu_usage": 13.45454545454544,
        "memory_total": 33369800704,
        "memory_used": 1823940608,
        "memory_percent": 6.7,
        "disk_total": 2162202353664,
        "disk_used": 23720402944,
        "disk_percent": 1.0970482436023694
    },
    {
        "id": 19,
        "hostname": "linux",
        "timestamp": "2025-04-06T18:01:14Z",
        "cpu_usage": 12.54545454545453,
        "memory_total": 33369800704,
        "memory_used": 1819013120,
        "memory_percent": 6.7,
        "disk_total": 2162202353664,
        "disk_used": 23720402944,
        "disk_percent": 1.0970482436023694
    }
]
```

## Database tables
![Host](./host_tablepng.png)
![SystemMetric](./systemmetric_table.png)


# SysMetrics Dashboard

The Dashboard app is a Django-based application that collects system metrics from agents and displays them on a central dashboard. Agents return real-time data such as system stats, which is then shown on the dashboard for easy monitoring and analysis.

The code for Dashboard is located under dashboard folder.




## Project Overview

## Prerequisites
- Python 3.8+
- Django 4.2+
- Requests library

## Setup Instructions

1. Clone the repository
```bash
git clone <repo-url>
cd sysmetrics/dashboard
```


2. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure Settings
- Ensure `http://127.0.0.1:8000/metrics` is accessible

5. Run Migrations
```bash
python manage.py migrate
```

6. Start the Development Server
```bash
python manage.py runserver 0.0.0.0:7000

In browser open url http://127.0.0.1:7000
```

## Project Structure
- `dashboard/`: Main application
  - `views.py`: Dashboard and processes views
  - `urls.py`: URL routing
  - `templates/`: HTML templates
  - `static/`: CSS and JavaScript files

## UI
![Processes Info](./processes.png)
![System Info](./sysinfo.png)
![Graph1](./graph1.png)
![Graph2](./graph2.png)
## Mobile Responsive
![Mobile Responsive](./mobile1.png)

##  To run both the Agent and Web Server

A script named `run.py` has been added.

- Use it after installing dependencies.
- Run the following command from sysmetrics folder:

```bash
python run.py
```

## Unit Tests
 - cd into sysmetrics folder and install all dependencies from requirements.txt using below command
 - python -m pip install -r requirements.txt 
 - cd into dashboard folder then run below commands
 - pytest core/tests/test_views.py -v
 - pytest metrics/tests/ -v
 - to run all unit tests at once run below command
 - pytest core/tests/ metrics/tests/ -v

## Unit Test results
 ![Unit Test results](./unit_test_output.png)

## Run tests with coverage
 - cd into sysmetrics folder and install all dependencies from requirements.txt using below command
 - python -m pip install -r requirements.txt 
 - cd into dashboard folder then run below commands
 - pytest --cov=core --cov=metrics --cov-report=html core/tests/ metrics/tests/ -v
 - This will create a directory called htmlcov with an index.html file you can open in your browser.

## Code Coverage results
 ![Code Coverage results](./code_cov_output.png)
## Notes
- Ensure your metrics API returns data in the expected JSON format
- Chart updates are handled client-side with JavaScript
