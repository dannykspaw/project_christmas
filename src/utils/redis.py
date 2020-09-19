# placeholder for potential redis integration for tracking pricing history
# auditing price history changes

# use a generated id for every model to avoid different product sku's being duplicates

'''

product base                - ornaments:ID                          24 character id
product property base       - ornaments:ID:PROPERTY                 price (could be expanded to support other properties)
product property history    - ornaments:ID:PROPERTY:history         ordered set (by timestamp) of changes to this property

'''