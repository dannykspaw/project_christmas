from utils.celery import app, tasks_formatter


# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#id5
tasks =  {
    'sync-yearly': {
        # the function that will execute this task
        'task': 'integrator.sync_by_vendor',
        # how often should this task be executed?
        'schedule': {
            # milliseconds, seconds, minutes, hours, days, weeks
            'seconds': 30,
        },
        'kwargs': {
            'vendor': 'hookedonhallmark_com'
        }
    }
}

timedelta_schedule = tasks_formatter(tasks)

# adds this schedule to the celery beat scheduler
# so it knows when to call functions
app.conf.beat_schedule = timedelta_schedule