import psycopg2
from .config import config


def connect():
    print('Connecting to postgres...')

    # connect to the db
    pg = config.postgres
    connect = psycopg2.connect(
        host = pg.host,
        database = pg.database,
        user = pg.user,
        password = pg.password
    )

    # create tables if they don't exist
    
    print(str(connect.closed).replace("0","Connected to {}...".format(pg.database)))

    # return the database cursor
    return connect.cursor()