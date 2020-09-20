# tells the integrator when to do stuff
# uses APScheduler with the SQLAlchemy backend connected to postgres to schedule jobs

from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor

import integrator
import integrations
from utils.config import config


def get_jobs():
    '''retrieves all jobs that need to be scheduled'''

    # yearly sync for every integration daily
    # once weekly check that all products have synced in the last day
    return [
        # demo: sync a single product for a single vendor
        {
            'method': integrator.sync_by_id,
            'args': ['123']
        },
        # demo: sync a single year of products for a single vendor
        {
            'method': integrator.sync_by_query,
            'args': [
                {
                    'vendor': integrations.hookedonhallmark_com,
                    'year': 1986
                }
            ]
        },
        # demo: sync a single year of products for all vendors
        {
            'method': integrator.sync_by_query,
            'args': [
                {
                    'year': 1986
                }
            ]
        },
    ]


def schedule_jobs(scheduler, jobs):
    '''provides all jobs to APScheduler to be scheduled'''

    for job in jobs:
        scheduler.add_job(
            func=job['method'],
            args=job['args'],

            # todo: create dot-notation helper
            # kwargs=job['kwargs'],
        )

    # todo: confirm if duplicates jobs are possible
    pass


if __name__ == "__main__":
    pg = config.postgres

    jobstores = {
        'default': SQLAlchemyJobStore(url='postgresql://{}:{}/{}'.format(pg.host, pg.port, pg.database))
    }
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }

    scheduler = BackgroundScheduler()
    scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)

    jobs = get_jobs()

    schedule_jobs(scheduler, jobs)
    scheduled_jobs = scheduler.get_jobs()