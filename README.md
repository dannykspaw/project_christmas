       _==_ _
     _,(",)|_|
      \/. \-|
    __( :  )|_

# project_christmas

#### architecture

![architecture](./images/architecture.png?raw=true "High-Level Architecture")

#### tasks
- [ ] integrations
    - [ ] all integration modules loaded on startup
        - [ ] remove './src/integrations/__init__.py' file
        - [ ] replace with process that loads all without explicityly naming each module
    - [x] prototypes
        - [x] hookedonhallmark_com
        - [x] ornament_shop_com
        - [x] hallmark_ornaments_com
    - [x] interface
        - [x] defined
            - get_ornaments_by_year(year)
            - get_ornament_by_url(url)
        - [x] using interface
            - [x] hookedonhallmark_com
            - [x] ornament_shop_com
            - [x] hallmark_ornaments_com
    - [ ] refactor
        - [ ] year links cached (using utils.redis)
        - [x] selenium webdriver creation abstracted to utils.selenium file
        - [ ] use global driver instance (utils.selenium.driver)
        - [ ] global driver is created for each integration
        - [ ] csv caching removed
- [ ] databases
    - [ ] postgresql
        - [x] utility module created
        - [x] connection parameterized using environment variables
        - [ ] initialization method
            - creates database?
            - creates tables from schema IF NOT EXISTS
        - [ ] logs piped to centralized location
    - [ ] redis
        - [x] utility module created
        - [ ] connection parameterized using environment variables
        - [ ] logs piped to centralized location
- [ ] integrator
    - [ ] can sync products from each integration
        - [ ] by id
        - [ ] by year
        - [ ] by vendor
    - [ ] can insert new products into database
- [ ] scheduler
    - [ ] celery configuration
    - [ ] 
- [ ] auditor
    - [ ] postgres "change streams" pubsub setup
        - [ ] setup process documented
        - [ ] setup process automated
    - [ ] audit functionality
        - [ ] price history is tracked over time
        - [ ] config to toggle more fields on
- [ ] server
    - [ ] routes
        - [ ] what are they?
    - [ ] authn/authz
        - api keys?

#### environment variables
```bash
ENV (optionsal) default is 'default'
CONFIG_PATH (optional) default is './config/$ENV.json'
```

#### data schemas
```sql

CREATE TABLE products (
    id VARCHAR(24) PRIMARY KEY,
    vendor VARCHAR(24) FOREIGN KEY,
    sku VARCHAR(20) NOT NULL,
    name VARCHAR(40) NOT NULL,
    price FLOAT NOT NULL,
    brand VARCHAR(40) NOT NULL,
    availability VARCHAR(10) NOT NULL,
    release_year VARCHAR(20) NOT NULL,
    vendor_id VARCHAR(20) NOT NULL,
    link VARCHAR(100) NOT NULL,
    last_synced_at DATE NOT NULL,
    created_at DATE NOT NULL,
)

```

#### setup
- start celery worker for integrator `celery -A integrator worker --loglevel=INFO`
- start celery scheduler `celery -A utils.celery beat`