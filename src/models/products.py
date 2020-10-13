import uuid
from re import sub
from decimal import Decimal
from datetime import datetime
from pandas import DataFrame

from utils.postgres import cursor, connect
from utils.celery import app


# todo: object to sql converter

# todo: logs with function metadata to allow for filtering by file-path
#       and simultaneously aggregating logs by service

# todo: create base model class/interface that takes a mapping of columns
#       and types and creates the tables in the database, as well as providing
#       helper functions for data conversion and an abstraction between the
#       psycopg2 module and any callers

# todo: access-control layer which sanitizes results from queries and restricts
#       who has access to which resources, the fields on those resources, as
#       well as the functions to modify them

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
    where_query = ' and '.join(['{} = \'{}\''.format(k, v) for k, v in query.items()])
    # limit_query = 'LIMIT {}'.format(limit) if limit else ''
    query = 'SELECT {} FROM products WHERE {}'.format(select_query, where_query)
    pg.execute(query)

    results = pg.fetchall()
    if len(results) == 0:
        return None

    return results


def find_one(query, projection):
    result = find(query, projection)
    if type(result) == list:
        return result[0]
    return result


@app.hooks
def create(new_product_dict):
    if type(new_product_dict) == dict:
        new_product_dict = [new_product_dict]
    
    values = []
    for new_product in new_product_dict:
        new_product['id'] = str(uuid.uuid1())
        new_product['created_at'] = datetime.utcnow()
        formatted_object = __format(new_product)
        value = __dict_to_values(formatted_object)
        values.append(value)

    if len(values) == 0:
        print('unable to create new products because length is 0')
        return

    columns_delimited = ','.join(columns)
    created = 0
    errored = 0

    for i in range(len(values)):
        insert_statement = 'INSERT INTO products ({}) VALUES {}'.format(columns_delimited, values[i])

        try:
            pg.execute(insert_statement)
            created += 1
        except Exception as err:
            print('unable to create product err {} sql {}'.format(err, insert_statement))
            errored += 1
            continue

    print('created {} product(s) and errored {} potential products'.format(created, errored))


@app.hooks
def update(query, update_object):
    obj = __format(update_object)
    set_query = ','.join(['{} = \'{}\''.format(k, v) for k, v in obj.items()])
    where_query = ' and '.join(['{} = \'{}\''.format(k, v) for k, v in query.items()])
    update_statement = 'UPDATE products SET {} WHERE {}'.format(set_query, where_query)

    try:
        pg.execute(update_statement)
    except Exception as err:
        print('unable to update product err {} sql {}'.format(err, update_statement))
        

def __format(new_object):
    try:
        new_object['last_synced_at'] = datetime.utcnow()
        new_object['price'] = Decimal(sub(r'[^\d.]', '', new_object['price']))
    except Exception as err:
        print('there was a problem while formatting product err {}'.format(err))
    return new_object


def __dict_to_values(dict):
    '''converts a dictionary and converts it's values into the values portion of an sql insert statement'''
    values = [None] * len(columns)
    for i in range(len(values)):
        values[i] = str(dict[columns[i]]).replace('\'', '\'\'')

    # https://repl.it/@terranblake/DeeppinkWeepyComputing#main.py
    result =  '(' + ','.join(['\'{}\''.format(x) for x in values]) + ')'
    return result