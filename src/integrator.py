# gets the data from the rich

# talk with each integration
# connect to the db to write new rows
# knows how to parameterize each integration
# uses audit util to keep track of price history
# creates ids using uuid.uuid1()

from utils.postgres import connect


postgres = connect()

def get_supported_integrations():
    '''returns a dictionary of all supported integrations'''
    pass

def sync_by_id(id=None):
    '''finds the product by id and calls the associated integration to update it using the product url'''
    pass

def sync_by_query(query=None):
    '''takes a dictionary of fields and values and generates an sql query from it'''
    pass