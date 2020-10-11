import uuid
from re import sub
from decimal import Decimal
from datetime import datetime
from pandas import DataFrame

from utils.postgres import cursor, connect


# todo: object to sql converter

# todo: create base model class/interface that takes a mapping of columns
#       and types and creates the tables in the database, as well as providing
#       helper functions for data conversion and an abstraction between the
#       psycopg2 module and any callers

# todo: access-control layer which sanitizes results from queries and restricts
#       who has access to which resources, the fields on those resources, as
#       well as the functions to modify them

# todo: event layer using celery job queues and the data access layer to create an
#       event-driven framework with support for pre/post hooks on all model signatures
#       and will dispatch events to subscribed processes if the function completes 
#       without error. you will subscribe using the exact same format as celery, which
#       will fire jobs to listeners on those functions. this simplifies the pubsub
#       model by using a thin data-access layer to publish jobs to subscribers using
#       a simple listener configuration

pg = cursor
columns = [
    'id',
    'vendor',
    'sku',
    'name',
    'price',
    'brand',
    'availability',
    'release_year',
    'link',
    'last_synced_at',
    'created_at'
]


def get(id, projection):
    select_statement = 'SELECT {} FROM products WHERE id = {};'.format(','.join(projection), id)
    pg.execute(select_statement)
    return pg.fetchone()


def find(query, projection):
    select_query = ','.join(projection)
    where_query = ' and '.join(['{} = {}' for k, v in query.items()])
    # limit_query = 'LIMIT {}'.format(limit) if limit else ''
    pg.execute('SELECT {} FROM products WHERE {}'.format(select_query, where_query))


def create(new_product_df):
    values = []
    for new_product in new_product_df.to_dict(orient='records'):
        formatted_object = __format(new_product)
        value = __dict_to_values(formatted_object)
        values.append(value)

    values_delimited = ','.join(values)
    columns_delimited = ','.join(columns)
    insert_statement = 'INSERT INTO products ({}) VALUES {}'.format(columns_delimited, values_delimited)
    print(insert_statement)

    pg.execute(insert_statement)
    connect.commit()


def update(query, update_object):
    set_query = ','.join(['{} = {}'.format(k, v) for k, v in update_object.items()])
    where_query = ' and '.join(['{} = {}'.format(k, v) for k, v in query.items()])
    pg.execute('UPDATE products SET {} WHERE {}'.format(set_query, where_query))


def __format(new_object):
    new_object['id'] = str(uuid.uuid1())
    new_object['last_synced_at'] = datetime.utcnow()
    new_object['created_at'] = datetime.utcnow()
    new_object['price'] = Decimal(sub(r'[^\d.]', '', new_object['price']))
    return new_object


def __dict_to_values(dict):
    '''converts a dictionary and converts it's values into the values portion of an sql insert statement'''
    values = [None] * len(columns)
    for i in range(len(values)):
        values[i] = str(dict[columns[i]]).replace('\'', '\'\'')

    # https://repl.it/@terranblake/DeeppinkWeepyComputing#main.py
    return '(' + ','.join(['\'{}\''.format(x) for x in values]) + ')'


