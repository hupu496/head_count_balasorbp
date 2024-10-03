from celery import Celery, shared_task
from celery.schedules import crontab

app = Celery()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls sync_monitor_data() every 10 minutes
    sender.add_periodic_task(600.0, sync_monitor_data.s(), name='sync_monitor_data every 10 minutes')
