from utils.celery import app, tasks_formatter


# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#id5
tasks =  {
    #name of the task for audit purposes
    # 'sync-integration-by-year-every-30-seconds': {
    #     # the function that will execute this task
    #     'task': 'integrator.sync_integration_by_year',
    #     # how often should this task be executed?
    #     'schedule': {
    #         # milliseconds, seconds, minutes, hours, days, weeks
    #         'seconds': 5,
    #     },
    #     'kwargs': {
    #         'integration_name': 'hookedonhallmark_com',
    #         'year': '1973'
    #     }
    # },
    # 'sync-all-integrations-by-year': {
    #     # the function that will execute this task
    #     'task': 'integrator.sync_by_year',
    #     # how often should this task be executed?
    #     'schedule': {
    #         # milliseconds, seconds, minutes, hours, days, weeks
    #         'minutes': 1,
    #         'seconds': 30,
    #     },
    #     'kwargs': {
    #         'year': '1974'
    #     }
    # },
    'sync-yearly': {
        # the function that will execute this task
        'task': 'integrator.sync_by_year',
        # how often should this task be executed?
        'schedule': {
            # milliseconds, seconds, minutes, hours, days, weeks
            'seconds': 30,
        },
        'kwargs': {
            # 'integration_name': 'ornament_shop_com',
            'year': '1977'
        }
    }
}

timedelta_schedule = tasks_formatter(tasks)

# adds this schedule to the celery beat scheduler
# so it knows when to call functions
app.conf.beat_schedule = timedelta_schedule