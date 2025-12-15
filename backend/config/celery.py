import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('market_supervision')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'aggregate-daily-stats': {
        'task': 'dashboard.tasks.aggregate_daily_statistics',
        'schedule': crontab(hour=1, minute=0),  # Run at 1 AM daily
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
