from datetime import datetime

from utils.celery import app
from utils.redis import store
from utils.config import config


# ornaments:MODEL:ID:FIELD
audit_history = 'ornaments:{}:{}:{}'

@app.job
def audit(id, args, **kwargs):
    try:
        _, model, __ = kwargs['task_name'].split('.')
        fields = set(args.keys()).union(set(config.hooks.audit[kwargs['audit_key']]))
        for field in fields:
            print('auditting field {} value {} on model {} id {}'.format(field, args[field], model, id))

            # from timestamp to date datetime.datetime.utcfromtimestamp(TIMESTAMP)
            set_key = audit_history.format(model, id, field)
            kvs = { args[field]: int(datetime.utcnow().timestamp()) }
            store.zadd(set_key, kvs)
    except Exception as err:
        print('unable to audit product id {} args {} kwargs {} err {}'.format(id, args, kwargs, err))