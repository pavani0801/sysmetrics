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

In browser open url http://localhost:8000/metrics
```