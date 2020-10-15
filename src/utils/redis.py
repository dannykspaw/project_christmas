import base64
import pickle
import json
import redis
from pprint import pprint

from .config import config

print('Connecting to redis...')
client = redis.StrictRedis(
    host=config.redis.host,
    port=config.redis.port,
    db=config.redis.db,
)

# celery queue
# l = client.lrange('celery', 0, -1)

# queued job count
# jobs_count = len(l)

# parse job as json
# job = json.loads(l[0])