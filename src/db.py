# handles connections and initialization of the db

from os import getenv

'''

export DB_HOST=localhost

'''

def connect():
    print('connecting to the db')
    # connect to the db
    print('host', getenv('DB_HOST'))

    # create tables if they don't exist

    # return the database cursor
    return None