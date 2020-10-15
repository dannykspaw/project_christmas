import os
import sys
import inspect
from functools import wraps
from celery import Celery, signals
from datetime import timedelta
import re

from .config import config

from pprint import pprint


@signals.worker_shutting_down.connect
def close(**kwargs):
    print('terminating celery session...')
    app.close()

    print('terminating postgres connection...')
    from .postgres import connect
    connect.close()

    print('terminating redis connection...')
    from .redis import store
    store.close()

    print('terminating webdriver executable...')
    from .selenium import driver
    driver.quit()


@signals.task_prerun.connect
def prehook(task_id=None, task=None, **kwargs):
    # pprint('pre-hook task {} id {} args {}'.format(task.name, task_id, kwargs['args']))
    return


@signals.task_postrun.connect
def posthook(task_id=None, task=None, **kwargs):
    # todo: abstract pre-post hooks behind module or simplify to array of functions to run before and after
    if len(config.hooks.audit.keys()) != 0:
        for pattern in config.hooks.audit.keys():
            # print('checking if task {} matches audit pattern {}'.format(task.name, pattern))
            if re.match(pattern, task.name) != None:
                priority = config.hooks.priority['auditor.audit']
                app.send_task('auditor.audit', args=kwargs['args'], kwargs=kwargs, priority=priority)
                break
    return


def __function_to_task_name(func, location):
    cwd = os.path.abspath(os.path.curdir)
    path = location.replace('{}/'.format(cwd), '')
    task_name = '{}.{}'.format(path.replace('/', '.'), func.__name__)
    task_name = task_name.replace('utils.celery', func.__module__)
    return task_name


def tasks_formatter(schedule):
    '''enumerates a dict of tasks and converts the schedule field into a timedelta instance'''
    for task_name, task in schedule.items():
        task_schedule = task['schedule']
        schedule[task_name]['schedule'] = __dict_to_timedelta(task_schedule)

    return schedule


def job(func):
    '''adds support for pre/post hooks on an incoming job'''
    task_location = os.path.abspath(inspect.getfile(func).replace('.py', ''))
    @wraps(func)
    def __hooks(*args, **kwargs):
        task_name = __function_to_task_name(func, task_location)
        try:
            priority = config.hooks.priority[task_name]
            print('publishing task {} priority {}'.format(task_name, priority))
            app.send_task(task_name, args=args, kwargs=kwargs, priority=priority)
        except Exception as err:
            print('unable to send async_task {} err {}'.format(task_name, err))

    app.task(func)
    return __hooks


def hooks(func):
    task_location = os.path.abspath(inspect.getfile(func).replace('.py', ''))

    '''adds support for publishing operations to functions by simply calling them'''
    @wraps(func)
    def __task(*args, **kwargs):
        task_name = __function_to_task_name(func, task_location)

        print('pre-hooks for task {} args {} kwargs {}'.format(task_name, args, kwargs))
        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as err:
            print('unable to call function for task', task_name, 'kwargs', kwargs, 'args', args, 'err', err)

        if len(config.hooks.audit.keys()) != 0:
            for pattern in config.hooks.audit.keys():
                if re.match(pattern, task_name) != None:
                    priority = config.hooks.priority['auditor.audit']
                    # print('auditting task {} args {} kwargs {}'.format(task_name, args, kwargs))
                    kwargs["task_name"] = task_name
                    kwargs["audit_key"] = pattern
                    app.send_task('auditor.audit', args=args, kwargs=kwargs, priority=priority)
                    break

        return result

    # register function with scheduler
    # location of the caller

    task_name = __function_to_task_name(func, task_location)
    app.task(func, name=task_name)
    return __task


def cleanup():
    app.close()


def __dict_to_timedelta(schedule_dict):
    '''takes a dictionary are returns a timedelta instance'''
    if type(schedule_dict) == type(timedelta):
        return schedule_dict

    return timedelta(**schedule_dict)

base = 'celery'
# if 'celery' in sys.argv[0]:
#     base = sys.argv[2]
# else:
#     base = sys.argv[0].replace('.py', '').replace('./', '')

print('Connecting to celery using base {}'.format(base))
redis = config.redis
app = Celery(base, broker='redis://{}:{}/'.format(redis.host, redis.port),)
app.conf.timezone = config.scheduler.timezone
app.hooks = hooks
app.job = job