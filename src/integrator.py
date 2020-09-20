from utils.config import config
from utils.postgres import connect

from integrations import *
import integrations


postgres = connect()

def sync_by_id(id=None):
    '''finds the product by id and calls the associated integration to update it using the product url'''

    # syncing by id implies that we already have a fully-qualified product object to pull a link from

    pass


def sync_by_query(query=None):
    '''takes a dictionary of fields and values and generates an sql query from it'''

    # different types of syncs
    # 1. existing product (syncing price and availability changes)
    # 2. new product (creates a completely new entry in the database)

    # is it better to have separate jobs for each type?
    # yes, have a scraping job created when a new product is found

    pass


def sync_by_url(vendor=None, url=None):
    '''takes a vendor and url and attempts to create a fully qualified product'''

    # take all new urls and put them in a list using a strategy from https://redis.io/topics/mass-insert
    # create a scheduled job that runs once every 30 minutes that iterates this new list and scrapes the new products

    # or make it really simple and scrape the page when it's found :shrug_emoji:

    pass


def __is_supported_integration(key=None):
    '''returns whether the provided key maps to a valid integration'''
    try:
        __import__('integrations.{}'.format(key), fromlist=[integrations])
    except ModuleNotFoundError:
        return False

    return True


def get_integration_by_name(key=None):
    '''returns the integration that corresponds to the key provided or returns false'''
    if __is_supported_integration(key) == False:
        raise Exception('integration {} is not supported'.format(key))

    return __import__('integrations.{}'.format(key), fromlist=[integrations])