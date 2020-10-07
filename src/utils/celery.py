from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

from .config import config


redis = config.redis
app = Celery('ornaments', broker='redis://{}:{}/'.format(redis.host, redis.port))
app.conf.timezone = 'UTC'

app.conf.beat_schedule = {
    'sync-every-hour': {
        'task': 'integrator.sync_by_id',
        'schedule': timedelta(seconds=10),
        'args': ('1')
    },
}