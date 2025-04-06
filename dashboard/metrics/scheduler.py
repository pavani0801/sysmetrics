# metrics/scheduler.py
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.conf import settings
from django.db import connection

from metrics.jobs import SystemMetricsJob

logger = logging.getLogger(__name__)

# Global variable to keep track of scheduler
scheduler = None

def close_db_connection():
    """
    Close the database connection to prevent connection leaks
    """
    connection.close()

def fetch_metrics():
    """
    Wrapper function to run the job and close DB connection
    """
    try:
        job = SystemMetricsJob(api_url=getattr(settings, 'METRICS_API_URL', None))
        job.run()
    finally:
        # Always close the connection after job runs
        close_db_connection()

def start():
    global scheduler
    
    # If scheduler already exists and running, don't start a new one
    if scheduler is not None and scheduler.running:
        return
    
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    
    # Try to gracefully handle database issues
    try:
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # Remove existing job if it exists to avoid conflicts
        try:
            scheduler.remove_job('fetch_system_metrics')
        except:
            pass  # Job doesn't exist yet, which is fine
        
        # Schedule job to run every 5 minutes
        scheduler.add_job(
            fetch_metrics,
            'interval',
            minutes=1,
            id='fetch_system_metrics',
            replace_existing=True,
            max_instances=1  # Prevent overlapping job executions
        )
        
        # Start the scheduler if it's not already running
        if not scheduler.running:
            logger.info("Starting scheduler...")
            scheduler.start()
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")