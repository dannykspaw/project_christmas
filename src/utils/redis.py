import base64
import pickle
import json
import redis

from .config import config

print('Connecting to redis...')

class Store(object):

    def __init__(self):
        self.client = redis.StrictRedis(
            host=config.redis.host,
            port=config.redis.port,
            db=config.redis.db,
            charset="utf-8",
            decode_responses=True
        )


    def get(self, key):
        value = self.client.get(key)
        return value

    
    def set(self, key, value):
        self.client.set(key, value)


    def set_to_expire(self, key, value, ttl):
        self.client.setex(key, ttl, value)


    def expire(self, key, ttl):
        self.client.expire(key, ttl)


    def sadd(self, set_key, values=[]):
        self.client.sadd(set_key, values)


    def smembers(self, set_key):
        values = self.client.smembers(set_key)
        return values

    
    def zadd(self, set_key, kv):
        self.client.zadd(set_key, kv)


    def match(self, pattern):
        values = self.client.keys(pattern)
        return values

    
    def close(self):
        self.client.close()


store = Store()
# celery queue
# l = client.lrange('celery', 0, -1)

# queued job count
# jobs_count = len(l)

# parse job as json
# job = json.loads(l[0])