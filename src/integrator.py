import sys
import pkgutil
from datetime import datetime

from utils.celery import app
from utils.postgres import cursor, connect
from models import products
import integrations


pg = cursor
integrations_list = [name for _, name, _ in pkgutil.iter_modules(['integrations'])]

def sync_by_id(id=None):
    '''finds the product by id and calls the associated integration to update it using the product url'''

    # 1. get the product in the database with this id
    product = products.get(id, ['id', 'vendor', 'price', 'availability'])

    # 2. get the integration that the product is associated with (get_integration_by_name)
    # integration_name = 'hallmark_ornaments_com'
    integration_name = product.vendor 

    # integration = integrations.hallmark_ornaments_com
    integration = get_integration_by_name(integration_name)

    # 3. use the integration to fetch the current product details
    synced_product = integration.sync_by_url(product.link)

    query_object = {
        'id': product.id,
    }

    update_object = {
        'price': synced_product.price,
        'availability': synced_product.availability,
        'last_synced_at': datetime.utcnow(),
    }

    # 4. update the database
    products.update(query_object, update_object)


def sync_integration_by_year(integration_name, year):
    integration = get_integration_by_name(integration_name)

    if year is None:
        raise Exception('unable to sync integration {} for year {} err please provide a year to sync'.format(integration_name, year))

    year = str(year)
    years = [str(x) for x in integration.year_links.keys()]

    if year not in years:
        raise Exception('unable to sync integration {} by year {} err integration does not support the provided year'.format(integration_name, year))

    print('syncing integration {} by year {}'.format(integration_name, year))
    n_products = None

    try:
        n_products = integration.get_ornaments_by_year(str(year))
    except Exception as err:
        print('unable to sync integration {} by year {} err {}'.format(integration_name, year, err))

    if n_products is None:
        raise Exception('unable to sync integration {} by year {} err no products were returned from integration'.format(integration_name, year))

    print('found {} products syncing integration {} by year {}'.format(n_products.shape[0], integration_name, year))

    # todo: handle duplicates -- lookup where (sku & vendor & year) to use unique index
    # if duplicate, update by id
    products.create(n_products)


def sync_by_year(year=None):
    '''takes a year and syncs all integrations by year'''
    for integration in integrations_list:
        try:
            sync_integration_by_year(integration, year)
        except:
            err = sys.exc_info()[0]
            print('unable to sync integration {} by year {} err {}'.format(integration, year, err))


def sync_by_vendor(vendor=None, year=None):
    '''takes a vendor and attempts to create a fully qualified product'''
    # get the integration module
    integration = get_integration_by_name(vendor)

    # get all years this integration supports
    years = [str(year)] if year != None else integration.year_links.keys()
    for year in years:
        sync_integration_by_year(vendor, year)


def sync_all():
    '''sync all integrations'''
    for integration in integrations_list:
        sync_by_vendor(integration)


def __is_supported_integration(key=None):
    '''returns whether the provided key maps to a valid integration'''
    return key in integrations_list


def get_integration_by_name(key=None):
    '''returns the integration that corresponds to the key provided or returns false'''
    if __is_supported_integration(key) == False:
        raise Exception('integration {} is not supported'.format(key))

    return __import__('integrations.{}'.format(key), fromlist=[integrations])


if __name__ == "__main__":
    sync_integration_by_year("hallmark_ornaments_com", 1976)