# project_christmas

#### environment variables
```bash
POSTGRES_HOST - (required)
POSTGRES_NAME - (required)
POSTGRES_USER - (required)
POSTGRES_PASSWORD - (required)
```

#### data schemas
```sql
CREATE TABLE products (
    id VARCHAR(24) PRIMARY KEY,
    sku VARCHAR(20) NOT NULL,
    name VARCHAR(40) NOT NULL,
    price FLOAT NOT NULL,
    brand VARCHAR(40) NOT NULL,
    availability VARCHAR(10) NOT NULL,
    release_year VARCHAR(20) NOT NULL,
    vendor_id VARCHAR(20) NOT NULL,
    vendor_name VARCHAR(20) NOT NULL,
    link VARCHAR(100) NOT NULL,
    synced_at DATE NOT NULL,
    created_at DATE NOT NULL,
)
```

#### setup
todo: outline steps to get running in a Docker container or to deploy everything into a cluster