from celery.schedules import crontab
from datetime import timedelta

from utils.celery import app


app.conf.beat_schedule = {
    'sync-every-hour': {
        'task': 'integrator.sync_by_id',
        'schedule': timedelta(seconds=5),
        'args': ('1')
    },
}