from os import path
import psycopg2
from .config import config
import psycopg2.extras


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
cursor = connect.cursor(cursor_factory = psycopg2.extras.DictCursor)

# drop tables to easily allow schema changes
# if config.env == 'default':
#     cursor.execute(open('{}/migrations/clean.sql'.format(path.curdir), 'r').read())

# create tables if they don't exist
cursor.execute(open('{}/migrations/create-tables.sql'.format(path.curdir), 'r').read())


def columns(table_name):
    cursor.execute('select column_name from information_schema.columns where table_name = \'{}\';'.format(table_name))
    results = cursor.fetchall()
    if results != None:
        results = [x[0] for x in results]
    return results