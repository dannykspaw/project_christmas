from utils.config import config
from utils.postgres import connect

from integrations import *
import integrations


postgres = connect()

def sync_by_id(id=None):
    '''finds the product by id and calls the associated integration to update it using the product url'''

    # 1. get the product in the database with this id
    # 2. get the integration that the product is associated with (get_integration_by_name)
    # 3. use the integration to fetch the current product details
    # 4. update the database

    pass


def sync_by_year(year=None):
    '''takes a year and syncs all vendors by year'''

    pass


def sync_by_vendor(vendor=None):
    '''takes a vendor and attempts to create a fully qualified product'''

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