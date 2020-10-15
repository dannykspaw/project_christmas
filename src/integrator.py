import sys
import pkgutil
from datetime import datetime

from utils.celery import app
from models import products
import integrations


integrations_list = [name for _, name, _ in pkgutil.iter_modules(['integrations'])]

def sync_by_id(id=None):
    '''finds the product by id and calls the associated integration to update it using the product url'''

    # 1. get the product in the database with this id
    product = products.get(id, ['id', 'vendor', 'price', 'availability'])
    
    # 2. get the integration that the product is associated with (get_integration_by_name)
    integration_name = product.vendor 
    integration = get_integration_by_name(integration_name)

    # 3. use the integration to fetch the current product details
    synced_product = None
    try:
        synced_product = integration.sync_by_url(product.link)
    except Exception as err:
        print('unable to sync integration {} by id {} err {}'.format(integration_name, id, err))
        return

    update_object = {
        'price': synced_product.price,
        'availability': synced_product.availability,
    }

    # 4. update the database
    products.update_one(id, update_object)


@app.job
def sync_integration_by_url(integration_name=None, url=None, year=None):
    integration = get_integration_by_name(integration_name)

    try:
        synced_product = integration.sync_by_url(url)
    except Exception as err:
        print('unable to sync integration {} by url {} err {}'.format(integration_name, url, err))
        return

    # todo: handle when the integration doesn't return a value

    find_query_object = {
        'vendor': integration_name,
        'link': url,
        'sku': synced_product['sku']
    }
    product = products.find_one(find_query_object, ['id'])
    if product is None:
        synced_product['release_year'] = year
        return products.create(synced_product)

    id = product[0]
    update_object = {
        'price': synced_product['price'],
        'availability': synced_product['availability'],
        'last_synced_at': datetime.utcnow(),
    }

    products.update_one(id, update_object)


@app.job
def sync_integration_by_year(integration_name, year):
    links_dict = {}
    integration = get_integration_by_name(integration_name)

    if year is None:
        raise Exception('unable to sync integration {} for year {} err please provide a year to sync'.format(integration_name, year))

    year = str(year)
    years = [str(x) for x in integration.year_links.keys()]

    if year not in years:
        raise Exception('unable to sync integration {} by year {} err integration does not support the provided year'.format(integration_name, year))

    print('syncing integration {} by year {}'.format(integration_name, year))
    
    links_dict = integration.get_ornaments_by_year(str(year))
    if links_dict is None:
        raise Exception('unable to sync integration {} by year {} err no products were returned from integration'.format(integration_name, year))

    print('found {} products syncing integration {} by year {}'.format(len(links_dict.keys()), integration_name, year))
    for _, link in links_dict.items():
        sync_integration_by_url(integration_name, link, year)


@app.job
def sync_by_year(year=None):
    '''takes a year and syncs all integrations by year'''
    for integration in integrations_list:
        sync_integration_by_year(integration, year)


@app.job
def sync_by_vendor(vendor=None, year=None):
    '''takes a vendor and attempts to create a fully qualified product'''
    # get the integration module
    integration = get_integration_by_name(vendor)

    # get all years this integration supports
    years = [str(year)] if year != None else integration.year_links.keys()
    for year in years:
        try:
            sync_integration_by_year(vendor, year)
        except Exception as err:
            print('unable to sync integration {} by year {} err {}'.format(vendor, year, err))


@app.task
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
    sync_by_vendor("hallmark_ornaments_com")
    # products.update_one('46597828-0e60-11eb-8a23-acde48001122', { 'price': 150 })
