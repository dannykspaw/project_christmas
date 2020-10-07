from celery.schedules import crontab
from datetime import timedelta

from utils.celery import app


# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#id5
app.conf.beat_schedule = {
    'sync-every-hour': {
        'task': 'integrator.sync_by_id',
        'schedule': timedelta(seconds=5),
        'args': ('1')
    },
}