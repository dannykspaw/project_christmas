columns = ['id', 'vendor', 'sku', 'name', 'price', 'brand',
           'availability', 'release_year', 'vendor_id', 'link', 'last_synced_at', 'created_at']

# todo: create base model class/interface that takes a mapping of columns
#       and types and creates the tables in the database, as well as providing
#       helper functions for data conversion and an abstraction between the
#       psycopg2 module and any callers