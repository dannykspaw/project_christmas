import pkgutil
from utils.config import config
from utils.postgres import cursor, connect

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
            availability = {}
        WHERE id = {}
    '''.format(price, availability, id))
    connect.commit()


def sync_integration_by_year(integration_name, year):
    integration = get_integration_by_name(integration_name)
    years = integration.year_links.keys()
    products = None

    if year in years:
        products = integration.get_ornaments_by_year(str(year))
    else:
        print('integration {} does not support year {}'.format(integration, year))
        return

    # todo: handle duplicates
    # if duplicate, update by id
    
    # build an insert statement for array of products
    values = ''
    for product in products.to_dict(orient='records'):
        value = ','.join(product.values())
        values += '({}),'.format(value)

    insert_statement = '''
        INSERT INTO 
            products (id, vendor, sku, name, price, brand, availability, release_year, vendor_id, link, last_synced_at, created_at)
        VALUES
            {}
    '''.format(values)

    print('inserting {} products into database'.format(len(products)))
    pg.execute(insert_statement)
    connect.commit()
    

def sync_by_year(year=None):
    '''takes a year and syncs all integrations by year'''
    integrations_list = [name for _, name, _ in pkgutil.iter_modules(['integrations'])]
    for integration in integrations_list:
        sync_integration_by_year(integration, year)


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


if __name__ == "__main__":
    sync_by_year('1975')