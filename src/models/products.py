from os import path
import uuid
from re import sub
from decimal import Decimal
from datetime import datetime

from utils.postgres import cursor, columns
from utils.celery import app
from utils.config import config


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
model = path.basename(__file__).replace('.py', '')
columns = columns(model)


@app.hooks
def get_by_id(id, projection):
    formatted_projection = ','.join(projection)
    select_statement = 'SELECT {} FROM {} WHERE id = {};'.format(formatted_projection, model, id)
    pg.execute(select_statement)

    result = pg.fetchone()
    return result


@app.hooks
def find(query, projection, limit=config.resources.limit):
    select_query = ','.join(projection)
    where_query = ' and '.join(['{} = \'{}\''.format(k, v) for k, v in query.items()])
    limit_query = ' LIMIT {}'.format(str(limit)) if limit else ''
    query = 'SELECT {} FROM {} WHERE {}{}'.format(select_query, model, where_query, limit_query)
    pg.execute(query)

    results = pg.fetchall()
    if len(results) == 0:
        return None

    return results


@app.hooks
def find_one(query, projection):
    result = find(query, projection, 1)
    if type(result) == list:
        result = result[0]
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
def update_one(id, update_object):
    obj = __format(update_object)
    set_query = ','.join(['{} = \'{}\''.format(k, v) for k, v in obj.items()])
    update_statement = 'UPDATE products SET {} WHERE id = \'{}\''.format(set_query, id)

    try:
        print('updating product id {}'.format(id))
        pg.execute(update_statement)
    except Exception as err:
        print('unable to update product err {} sql {}'.format(err, update_statement))
        return


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
        return
        

def __format(new_object):
    try:
        new_object['last_synced_at'] = datetime.utcnow()
        new_object['price'] = Decimal(sub(r'[^\d.]', '', str(new_object['price'])))
    except Exception as err:
        print('there was a problem while formatting product err {}'.format(err))
    return new_object


def __dict_to_values(dict):
    '''converts a dictionary and converts it's values into the values portion of an sql insert statement'''
    try:
        values = [None] * len(columns)
        for i in range(len(values)):
            values[i] = str(dict[columns[i]]).replace('\'', '\'\'')

        # https://repl.it/@terranblake/DeeppinkWeepyComputing#main.py
        result =  '(' + ','.join(['\'{}\''.format(x) for x in values]) + ')'
    except Exception as err:
        print('unable to convert dict {} to values err {}'.format(dict, err))
        return

    return result