from os import path
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

    cursor = connect.cursor()

    # create tables if they don't exist
    cursor.execute(open('{}/src/migrations/create-tables.sql'.format(path.curdir), 'r').read())
    
    print(str(connect.closed).replace("0","Connected to {}...".format(pg.database)))

    # return the database cursor
    return cursor