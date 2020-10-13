import os
import inspect
from functools import wraps
from celery import Celery, signals
from datetime import timedelta
import atexit

from .config import config


@signals.task_prerun.connect
def prehook(task_id=None, task=None, **kwargs):
    # print('pre-hook task {} id {} args {}'.format(task.name, task_id, kwargs['args']))
    return


@signals.task_postrun.connect
def posthook(task_id=None, task=None, **kwargs):
    # print('post-hook task {} id {} args {}'.format(task.name, task_id, kwargs['args']))
    return


def __function_to_task_name(func, location):
    cwd = os.path.abspath(os.path.curdir)
    path = location.replace('{}/'.format(cwd), '')
    task_name = '{}.{}'.format(path.replace('/', '.'), func.__name__)
    return task_name


def tasks_formatter(schedule):
    '''enumerates a dict of tasks and converts the schedule field into a timedelta instance'''
    for task_name, task in schedule.items():
        task_schedule = task['schedule']
        schedule[task_name]['schedule'] = __dict_to_timedelta(task_schedule)

    return schedule


def async_task(func):
    '''adds support for pre/post hooks on an incoming job'''
    task_location = os.path.abspath(inspect.getfile(func).replace('.py', ''))
    @wraps(func)
    def __hooks(*args, **kwargs):
        task_name = __function_to_task_name(func, task_location)
        task_name = task_name.replace('utils.celery', func.__module__)
        try:
            # print('publishing task {}'.format(task_name))
            app.send_task(task_name, args=args, kwargs=kwargs)
        except Exception as err:
            print('exception for task {} err {}'.format(task_name, err))

    app.task(func)
    print('registered task {}'.format(__function_to_task_name(func, task_location)))
    return __hooks


def hooks(func):
    task_location = os.path.abspath(inspect.getfile(func).replace('.py', ''))

    '''adds support for publishing operations to functions by simply calling them'''
    @wraps(func)
    def __task(*args, **kwargs):
        task_name = __function_to_task_name(func, task_location)

        # print('pre-hooks for task {}'.format(task_name))
        result = None
        try:
            # print('calling function for task {}'.format(task_name))
            result = func(*args, **kwargs)
        except Exception as err:
            print('unable to call function for task', task_name, 'err', err)

        # print('post-hooks for task {}'.format(task_name))
        return result

    # register function with scheduler
    # location of the caller
    app.task(func)
    return __task


def cleanup():
    app.close()


def __dict_to_timedelta(schedule_dict):
    '''takes a dictionary are returns a timedelta instance'''
    if type(schedule_dict) == type(timedelta):
        return schedule_dict

    return timedelta(**schedule_dict)


redis = config.redis
app = Celery('ornaments', broker='redis://{}:{}/'.format(redis.host, redis.port))
app.conf.timezone = config.scheduler.timezone
app.hooks = hooks
app.async_task = async_task