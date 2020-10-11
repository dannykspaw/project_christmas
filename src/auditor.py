from utils.events import bus


# tracks changes in the database and audits them
# use a generated id for every model to avoid different product sku's being duplicates

'''

product base                - ornaments:ID                          24 character id
product property base       - ornaments:ID:PROPERTY                 price (could be expanded to support other properties)
product property history    - ornaments:ID:PROPERTY:history         ordered set (by timestamp) of changes to this property

'''

listeners = {
    # name of the task for audit purposes
    'audit-product-price-history': {
        # the function to listen to
        'subscription': 'models.products.update',
        # the function which handles the event
        'handler': 'auditor.audit',
        # the query to filter objects (only works on model functions)
        # e.g. only auditing updates to price which happens to use a 
        #       special flag that gets set for each field that was changed
        'query': {
            'price': '$changed'
        }
    }
}

bus.add_listeners(listeners)