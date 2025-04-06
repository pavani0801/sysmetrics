# metrics/models.py
from django.db import models

class Host(models.Model):
    hostname = models.CharField(max_length=255, unique=True)
    ip_address = models.CharField(max_length=50)
    os_info = models.CharField(max_length=255)
    cpu_cores = models.IntegerField()
    
    def __str__(self):
        return self.hostname

class SystemMetric(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='metrics')
    timestamp = models.DateTimeField()
    
    # CPU metrics
    cpu_usage = models.FloatField(help_text="Overall CPU usage percentage")
    
    # Memory metrics
    memory_total = models.BigIntegerField(help_text="Total memory in bytes")
    memory_used = models.BigIntegerField(help_text="Used memory in bytes")
    memory_percent = models.FloatField(help_text="Memory usage percentage")
    
    # Disk metrics
    disk_total = models.BigIntegerField(help_text="Total disk space in bytes")
    disk_used = models.BigIntegerField(help_text="Used disk space in bytes") 
    disk_percent = models.FloatField(help_text="Disk usage percentage")
    
    class Meta:
        indexes = [
            models.Index(fields=['host', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.host.hostname} - {self.timestamp}"