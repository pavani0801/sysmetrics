import psutil
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn
from typing import Dict, List, Any
import platform
import socket
from pydantic import BaseModel


app = FastAPI(
    title="Linux Metrics Agent",
    description="Agent for collecting system metrics on Linux hosts",
    version="1.0.0"
)


class MetricsResponse(BaseModel):
    timestamp: str
    hostname: str
    ip_address: str
    os_info: str
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    processes: List[Dict[str, Any]]

# Get host information
def get_host_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    os_info = f"{platform.system()} {platform.release()}"
    return hostname, ip_address, os_info

# Get CPU metrics
def get_cpu_metrics():
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    cpu_times = psutil.cpu_times_percent(interval=1)
    
    return {
        "percent_usage_per_core": cpu_percent,
        "overall_usage": sum(cpu_percent) / len(cpu_percent),
        "user": cpu_times.user,
        "system": cpu_times.system,
        "idle": cpu_times.idle,
        "cores": psutil.cpu_count(logical=True),
        "physical_cores": psutil.cpu_count(logical=False)
    }

# Get memory metrics
def get_memory_metrics():
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    return {
        "total": memory.total,
        "available": memory.available,
        "used": memory.used,
        "free": memory.free,
        "percent_used": memory.percent,
        "swap_total": swap.total,
        "swap_used": swap.used,
        "swap_percent": swap.percent
    }

# Get disk metrics
def get_disk_metrics():
    partitions = psutil.disk_partitions()
    disk_data = []
    
    for partition in partitions:
        if partition.fstype:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_data.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent_used": usage.percent
            })
    
    # Get overall IO stats
    io_counters = psutil.disk_io_counters()
    io_stats = {
        "read_count": io_counters.read_count if io_counters else 0,
        "write_count": io_counters.write_count if io_counters else 0,
        "read_bytes": io_counters.read_bytes if io_counters else 0,
        "write_bytes": io_counters.write_bytes if io_counters else 0
    }
    
    return {
        "partitions": disk_data,
        "io_stats": io_stats
    }

# Get process information
def get_process_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time', 'status']):
        try:
            # Get process information
            process_info = proc.info
            # Add command line if available
            try:
                process_info['cmdline'] = ' '.join(proc.cmdline())
            except (psutil.AccessDenied, psutil.ZombieProcess):
                process_info['cmdline'] = "Access Denied"
            
            # Format create time
            if 'create_time' in process_info:
                process_info['create_time'] = datetime.fromtimestamp(
                    process_info['create_time']
                ).strftime('%Y-%m-%d %H:%M:%S')
            
            processes.append(process_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sort processes by CPU usage (descending)
    processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
    return processes

@app.get("/", response_model=dict)
async def root():
    """Root endpoint that returns basic information about the API."""
    return {
        "message": "Linux Metrics Agent",
        "endpoints": {
            "/metrics": "Get full system metrics",
            "/metrics/cpu": "Get CPU metrics only",
            "/metrics/memory": "Get memory metrics only",
            "/metrics/disk": "Get disk metrics only",
            "/metrics/processes": "Get process information only"
        }
    }

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get all system metrics including CPU, memory, disk and process information."""
    try:
        hostname, ip_address, os_info = get_host_info()
        
        return {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "hostname": hostname,
            "ip_address": ip_address,
            "os_info": os_info,
            "cpu": get_cpu_metrics(),
            "memory": get_memory_metrics(),
            "disk": get_disk_metrics(),
            "processes": get_process_info()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting metrics: {str(e)}")

@app.get("/metrics/cpu")
async def get_cpu():
    """Get CPU metrics only."""
    try:
        return {"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "cpu": get_cpu_metrics()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting CPU metrics: {str(e)}")

@app.get("/metrics/memory")
async def get_memory():
    """Get memory metrics only."""
    try:
        return {"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "memory": get_memory_metrics()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting memory metrics: {str(e)}")

@app.get("/metrics/disk")
async def get_disk():
    """Get disk metrics only."""
    try:
        return {"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "disk": get_disk_metrics()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting disk metrics: {str(e)}")

@app.get("/metrics/processes")
async def get_processes():
    """Get process information only."""
    try:
        return {"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "processes": get_process_info()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting process information: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)