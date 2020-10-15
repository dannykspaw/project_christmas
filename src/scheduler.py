from utils.celery import app, tasks_formatter


# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#id5
tasks =  {
    'sync-yearly': {
        # the function that will execute this task
        'task': 'integrator.sync_by_integration',
        # how often should this task be executed?
        'schedule': {
            # milliseconds, seconds, minutes, hours, days, weeks
            'seconds': 30,
        },
        'kwargs': {
            'integration_name': 'hookedonhallmark_com'
        }
    }
}

timedelta_schedule = tasks_formatter(tasks)
app.conf.beat_schedule = timedelta_schedule