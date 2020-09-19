# tells the integrator when to do stuff
# uses APScheduler with the SQLAlchemy backend connected to postgres to schedule jobs


def get_tasks():
    '''retrieves all tasks that need to be scheduled'''

    # yearly sync for every integration daily
    pass

def schedule_tasks(tasks=None):
    '''provides all tasks to APScheduler to be scheduled'''

    # todo: confirm if duplicates jobs are possible
    pass


if __name__ == "__main__":
    pass