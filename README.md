       _==_ _
     _,(",)|_|
      \/. \-|
    __( :  )|_

# project_christmas

#### architecture

![architecture](./images/architecture.png?raw=true "High-Level Architecture")

#### tasks
- [ ] integrations
    - [ ] refactor
        - [ ] year links cached (using utils.redis)
- [ ] server
    - [ ] routes
        - [ ] what are they?
    - [ ] authn/authz
        - api keys?
- [ ] tests
    - [ ] integrator
    - [ ] integrations
    - [ ] scheduler
    - [ ] auditor

#### environment variables
```bash
ENV (optionsal) default is 'default'
CONFIG_PATH (optional) default is './config/$ENV.json'
```

#### data schemas
```sql

CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(24) PRIMARY KEY,
    vendor VARCHAR(24) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    name VARCHAR(40) NOT NULL,
    price FLOAT NOT NULL,
    brand VARCHAR(40) NOT NULL,
    availability VARCHAR(10) NOT NULL,
    release_year VARCHAR(20) NOT NULL,
    vendor_id VARCHAR(20) NOT NULL,
    link VARCHAR(100) NOT NULL,
    last_synced_at DATE NOT NULL,
    created_at DATE NOT NULL
)

```

#### setup
- navigate to `./src/` folder
- start celery scheduler `celery -A scheduler beat`
- start celery worker `celery -A integrator worker --loglevel=INFO --concurrency=1 -n worker1@%h`