from os import path
import psycopg2
from .config import config

print('Connecting to postgres...')

# connect to the db
pg = config.postgres
connect = psycopg2.connect(
    host = pg.host,
    database = pg.database,
    user = pg.user,
    password = pg.password
)
connect.autocommit = True

print(str(connect.closed).replace("0","Connected to {}...".format(pg.database)))
cursor = connect.cursor()

# drop tables to easily allow schema changes
# if config.env == 'default':
#     cursor.execute(open('{}/migrations/clean.sql'.format(path.curdir), 'r').read())

# create tables if they don't exist
cursor.execute(open('{}/migrations/create-tables.sql'.format(path.curdir), 'r').read())


def cleanup():
    connect.close()