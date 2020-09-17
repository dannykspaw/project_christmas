# project_christmas

#### data schema
```json
// product
{
    "Product Code": "string",
    "Product Name": "string",
    "Product Price": "float",
    "Product Brand": "string",
    "Product Availability": "string",
    "Product Id": "string",
    "Product Release Year": "integer",
    "Product Vendor": "string"
}
```

#### folder structure
```bash
src/
    integrator.py       - handles communicating with integrations, syncing pricing and availability changes
    server.py           - exposes the dataset through an api
integrations/           - contains scripts with a consistent interface to retrieve updates from each data source
    data-source-1.py
    data-source-2.py
seed/                   - contains a dataset from each data source to seed the database with
    data-source-1.csv
    
```

### integrations
ornament-shop.com
- [x] get links for every year
- [x] get products by year
- [x] get product details using product link
- [x] cache product details in csv

hookedonhallmark.com
- [x] get links for every year
- [x] get products by year
    - [x] The by-year links shown on the yearly page don't account for segmented ornaments, breaking product acquisition, returning a very low number or no products at all to scrape
- [x] get product details using product link
- [x] cache product details in csv