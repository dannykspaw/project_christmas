# handles connections and initialization of the db

from os import getenv
import psycopg2


def connect():
    print('connecting to the db')
    connect = psycopg2.connect(
    host = getenv('DB_HOST'),
    database = getenv('DB_NAME'),
    user = getenv('DB_USER'),
    password = getenv('DB_PASSWORD')
    )
    print('host', getenv('DB_HOST'))
    print('database', getenv('DB_NAME'))
    print('user', getenv('DB_USER'))
    print('password', getenv('DB_PASSWORD'))
    # create tables if they don't
    # return the database cursor
    print(str(cursor.closed).replace("0","Connected to {}...".format(getenv('DB_NAME'))))
    return connect.cursor()
connect()
