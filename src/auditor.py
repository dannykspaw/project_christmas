from datetime import datetime

from utils.celery import app
from utils.redis import client
from utils.config import config


# ornaments:MODEL:ID:FIELD
audit_history = 'ornaments:{}:{}:{}'

@app.job
def audit(id, args, **kwargs):
    _, model, __ = kwargs['task_name'].split('.')
    fields = set(args.keys()).union(set(config.hooks.audit[kwargs['audit_key']]))
    for field in fields:
        print('auditting field {} value {} on model {} id {}'.format(field, args[field], model, id))

        # from timestamp to date datetime.datetime.utcfromtimestamp(TIMESTAMP)
        client.zadd(audit_history.format(model, id, field), { args[field]: datetime.utcnow().timestamp() })