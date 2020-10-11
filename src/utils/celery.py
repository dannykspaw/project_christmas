from functools import wraps
from celery import Celery
from datetime import timedelta

from .config import config


def tasks_formatter(schedule):
    '''enumerates a dict of tasks and converts the schedule field into a timedelta instance'''
    for task_name, task in schedule.items():
        task_schedule = task['schedule']
        schedule[task_name]['schedule'] = __dict_to_timedelta(task_schedule)

    return schedule


def hooks(func):
    '''adds support for pre/post operations on function decorated with this decorator'''
    # todo: get pre/post handlers by dot-notation
    #       module name and run accordingly
    @wraps(func)
    def hooks(*args, **kwargs):
        print('pre-hook for decorated function')
        func(*args, **kwargs)

    return hooks


def __dict_to_timedelta(schedule_dict):
    '''takes a dictionary are returns a timedelta instance'''
    if type(schedule_dict) == type(timedelta):
        return schedule_dict

    return timedelta(**schedule_dict)


redis = config.redis
app = Celery('ornaments', broker='redis://{}:{}/'.format(redis.host, redis.port))
app.conf.timezone = config.scheduler.timezone
app.async_task = hooks