import pkgutil
import uuid
from datetime import datetime
from re import sub
from decimal import Decimal

from utils.config import config
from utils.postgres import cursor, connect
from utils.celery import app

from models import products
from integrations import *
import integrations


pg = cursor

def sync_by_id(id=None):
    '''finds the product by id and calls the associated integration to update it using the product url'''

    # 1. get the product in the database with this id
    pg.execute('SELECT id, vendor, price, availability FROM products WHERE id = {};'.format(id))
    product = pg.fetchone()

    # 2. get the integration that the product is associated with (get_integration_by_name)
    # integration_name = 'hallmark_ornaments_com'
    integration_name = product.vendor 

    # integration = integrations.hallmark_ornaments_com
    integration = get_integration_by_name(integration_name)

    # 3. use the integration to fetch the current product details
    link = product.link
    synced_product = integration.sync_by_url(link)

    # 4. update the database
    price = product.price
    if synced_product.price != price:
        price = synced_product.price

    availability = product.availability
    if synced_product.availability != availability:
        availability = synced_product.availability

    pg.execute('''
        UPDATE products
        SET
            price = {},
            availability = {},
            last_synced_at = {},
        WHERE id = {}
    '''.format(price, availability, datetime.utcnow(), id))
    connect.commit()


def sync_integration_by_year(integration_name, year):
    print('syncing integration {} by year {}'.format(integration_name, year))

    integration = get_integration_by_name(integration_name)
    years = integration.year_links.keys()
    n_products = None

    if year in years:
        n_products = integration.get_ornaments_by_year(str(year))
    else:
        print('integration {} does not support year {}'.format(integration, year))
        return

    if n_products is None:
        print('no products were returned from integration {} bailing!'.format(integration_name))
        return

    # todo: handle duplicates -- lookup where (sku & vendor & year) <- index?
    # if duplicate, update by id
    
    # build an insert statement for array of products
    values = []
    for product in n_products.to_dict(orient='records'):
        # extract just the decimal from the price $29.99 -> 29.99
        product['price'] = Decimal(sub(r'[^\d.]', '', product['price']))
        product['id'] = str(uuid.uuid1())
        product['last_synced_at'] = datetime.utcnow()
        product['created_at'] = datetime.utcnow()

        value = __dict_to_values(product)
        values.append(value)

    # todo: create a models folder that defines the columns and operations
    insert_statement = 'INSERT INTO products ({}) VALUES {}'.format(','.join(products.columns), ','.join(values))

    print('inserting {} products into database'.format(len(n_products)))
    pg.execute(insert_statement)
    connect.commit()


def sync_by_year(year=None):
    '''takes a year and syncs all integrations by year'''
    integrations_list = [name for _, name, _ in pkgutil.iter_modules(['integrations'])]
    for integration in integrations_list:
        sync_integration_by_year(integration, year)


def sync_by_vendor(vendor=None, year=None):
    '''takes a vendor and attempts to create a fully qualified product'''
    # get the integration module
    integration = get_integration_by_name(vendor)

    # get all years this integration supports
    years = [str(year)] if year != None else integration.year_links.keys()
    for year in years:
        sync_integration_by_year(vendor, year)


def __dict_to_values(dict):
    '''converts a dictionary and converts it's values into the values portion of an sql insert statement'''
    # https://repl.it/@terranblake/DeeppinkWeepyComputing#main.py
    return '(' + ','.join(['\'{}\''.format(x) for x in dict.values()]) + ')'


def __is_supported_integration(key=None):
    '''returns whether the provided key maps to a valid integration'''
    return key in [name for _, name, _ in pkgutil.iter_modules(['integrations'])]


def get_integration_by_name(key=None):
    '''returns the integration that corresponds to the key provided or returns false'''
    if __is_supported_integration(key) == False:
        raise Exception('integration {} is not supported'.format(key))

    return __import__('integrations.{}'.format(key), fromlist=[integrations])
