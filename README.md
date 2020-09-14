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
    "Product Release Year": "integer"
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