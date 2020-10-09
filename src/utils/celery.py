from celery import Celery
from .config import config


redis = config.redis
app = Celery('ornaments', broker='redis://{}:{}/'.format(redis.host, redis.port))
app.conf.timezone = config.scheduler.timezone