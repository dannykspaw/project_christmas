import sys
import pkgutil
from datetime import datetime, date

from utils.celery import app, __dict_to_timedelta
from utils.redis import store
from utils.config import config
from utils.selenium import driver

from models import products
import integrations

sync_interval = __dict_to_timedelta(config.integrator.sync.interval)
integrations_list = [name for _, name, _ in pkgutil.iter_modules(['integrations'])]

# @app.job
def sync_by_id(id=None):
    '''finds the product by id and calls the associated integration to update it using the product url'''

    # 1. get the product in the database with this id
    product = products.get_by_id(id, ['id', 'vendor', 'price', 'availability', 'link', 'last_synced_at'])
    if product != None:
        # only sync using an id so we can lookup using the unique id
        # raise Exception('unable to sync integration {} by url {} err product not found in database'.format(integration_name, url))

        # the integration doesn't need to be synced again
        # print(datetime.fromtimestamp(product[1]), type(datetime.fromtimestamp(product[1])))
        if (product['last_synced_at'] + sync_interval) > datetime.now():
            print('skipping sync product id {} because it was synced in the last {}'.format(product.id, sync_interval))
            return
    
    # 2. get the integration that the product is associated with (get_integration_by_name)
    integration_name = product['vendor'] 
    integration = get_integration_by_name(integration_name)

    # 3. use the integration to fetch the current product details
    synced_product = None
    try:
        driver.refresh()
        synced_product = integration.sync_by_url(product['link'])
    except Exception as err:
        print('unable to sync integration {} by id {} err {}'.format(integration_name, id, err))
        return

    update_object = {
        'price': synced_product['price'],
        'availability': synced_product['availability'],
    }

    # 4. update the database
    products.update_one(id, update_object)


@app.job
def sync_integration_by_url(integration_name=None, url=None, year=None):
    find_query_object = {
        'vendor': integration_name,
        'link': url,
        # todo: figure out why the release year for some objects aren't what we're passing in here
        # 'release_year': str(year)
    }
    product = products.find_one(find_query_object, ['id', 'last_synced_at'])
    if product != None:
        # only sync using an id so we can lookup using the unique id
        # raise Exception('unable to sync integration {} by url {} err product not found in database'.format(integration_name, url))

        # the integration doesn't need to be synced again
        # print(datetime.fromtimestamp(product[1]), type(datetime.fromtimestamp(product[1])))
        if (product['last_synced_at'] + sync_interval) > datetime.now():
            print('skipping sync product id {} because it was synced in the last {}'.format(product['id'], sync_interval))
            return

    integration = get_integration_by_name(integration_name)

    try:
        driver.refresh()
        synced_product = integration.sync_by_url(url)
    except Exception as err:
        print('unable to sync integration {} by url {} err {}'.format(integration_name, url, err))
        return

    # todo: handle when the integration doesn't return a value
    product = products.find_one(find_query_object, ['id'])
    if product is None:
        synced_product['release_year'] = year
        return products.create(synced_product)

    update_object = {
        'price': synced_product['price'],
        'availability': synced_product['availability'],
        'last_synced_at': datetime.utcnow(),
    }

    products.update_one(product['id'], update_object)


@app.job
def sync_integration_by_year(integration_name, year):
    links_dict = {}
    integration = get_integration_by_name(integration_name)

    cache_key =   'cache:integration:{}:links:year:{}'.format(integration_name, year)
    year = str(year)
    # todo: abstract this behind an integration hook
    year_link = store.get(cache_key)
    if year_link == None:
        raise Exception('unable to sync integration {} for year {} err no year link found'.format(integration_name, year))

    print('syncing integration {} by year {} link {}'.format(integration_name, year, year_link))
    driver.refresh()
    links_dict = integration.get_ornaments_by_year(year, year_link)
    if links_dict is None:
        raise Exception('unable to sync integration {} by year {} err no products were returned from integration'.format(integration_name, year))

    print('found {} products syncing integration {} by year {}'.format(len(links_dict.keys()), integration_name, year))
    for _, link in links_dict.items():
        sync_integration_by_url(integration_name, link, year)


@app.job
def sync_by_year(year=None):
    '''takes a year and syncs all integrations by year'''
    for integration in integrations_list:
        sync_integration_by_year(integration, str(year))


@app.job
def sync_by_integration(integration_name=None):
    '''takes a integration_name and attempts to create a fully qualified product'''

    integration = get_integration_by_name(integration_name)
    driver.refresh()
    links_dict = integration.get_year_links()

    integration_links_key = 'cache:integration:{}:links:years'.format(integration_name)
    one_week = 60 * 60 * (24 * 7)

    # get the integration module
    # todo: abstract this behind an integration hook
    for year, link in links_dict.items():
        integration_link_cache_key = 'cache:integration:{}:links:year:{}'.format(integration_name, year)
        # refresh year links weekly
        store.set_to_expire(integration_link_cache_key, link, one_week)
        store.sadd(integration_links_key, year)
        store.expire(integration_links_key, one_week)

        try:
            sync_integration_by_year(integration_name, year)
        except Exception as err:
            print('unable to sync integration {} by year {} err {}'.format(integration_name, year, err))


@app.task
def sync_all():
    '''sync all integrations'''
    for integration in integrations_list:
        sync_by_integration(integration)


# todo: sync all should have the ability to sync
#       with only an id
# @app.task
# def sync_all():
#     '''sync all integrations'''
#     for integration in integrations_list:
#         sync_by_integration(integration)


def __is_supported_integration(key=None):
    '''returns whether the provided key maps to a valid integration'''
    return key in integrations_list


def get_integration_by_name(key=None):
    '''returns the integration that corresponds to the key provided or returns false'''
    if __is_supported_integration(key) == False:
        raise Exception('integration {} is not supported'.format(key))

    return __import__('integrations.{}'.format(key), fromlist=[integrations])


if __name__ == "__main__":
    # all
    # sync_all()

    # by integration
    # sync_by_integration('hallmark_ornaments')

    # by year
    # sync_integration_by_year('hallmark_ornaments', 2004)

    # by id
    # sync_by_id('52b481ee-0e60-11eb-8a23-acde48001122')

    # update product
    # update_object = {
    #     'price': '$3.98',
    #     'availability': 'In Stock - Ships Next Business Day',
    #     'last_synced_at': '2020-10-17 17:06:40.884777'
    # }
    # products.update_one('67e3cfcc-0fd5-11eb-82c0-acde48001122', update_object)
    pass