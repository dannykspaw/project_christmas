from utils.celery import app, tasks_formatter


# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#id5
tasks =  {
    'sync-by-year-every-hour': {
        'task': 'integrator.sync_by_year',
        'schedule': {
            'seconds': 5
        },
        'kwargs': {
            'year': '1973'
        }
    },
}

timedelta_schedule = tasks_formatter(tasks)

# adds this schedule to the celery beat scheduler
# so it knows when to call functions
app.conf.beat_schedule = timedelta_schedule