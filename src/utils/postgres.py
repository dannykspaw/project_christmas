from os import getenv
import psycopg2


def connect():
    print('connecting to the db')
    connect = psycopg2.connect(
        host = getenv('POSTGRES_HOST'),
        database = getenv('POSTGRES_NAME'),
        user = getenv('POSTGRES_USER'),
        password = getenv('POSTGRES_PASSWORD')
    )
    print('host', getenv('POSTGRES_HOST'))
    print('database', getenv('POSTGRES_NAME'))
    print('user', getenv('POSTGRES_USER'))
    print('password', getenv('POSTGRES_PASSWORD'))
    # create tables if they don't
    # return the database cursor
    print(str(connect.closed).replace("0","Connected to {}...".format(getenv('POSTGRES_DATABASE'))))
    return connect.cursor()