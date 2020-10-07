       _==_ _
     _,(",)|_|
      \/. \-|
    __( :  )|_

# project_christmas

#### architecture

![architecture](./images/architecture.png?raw=true "High-Level Architecture")

#### tasks
- [ ] integrations
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
    - [ ] redis
        - [x] utility module created
        - [ ] connection parameterized using environment variables
- [ ] integrator
    - [ ] can sync products from each integration
        - [ ] by id
        - [ ] by year
        - [ ] by vendor
        - [ ] by query
    - [ ] can insert new products into database
- [ ] scheduler
    - [x] celery configuration
    - [ ] setup reccurring tasks
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
- start celery worker for integrator `celery -A integrator worker --loglevel=INFO`
```shell
loading default config from /Users/tblake/Documents/project_christmas/src/config
Connecting to postgres...
Connected to ornaments...
 
 -------------- celery@terrans-mbp-2.lan v5.0.0 (singularity)
--- ***** ----- 
-- ******* ---- macOS-10.15.6-x86_64-i386-64bit 2020-10-07 14:43:44
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         ornaments:0x103785880
- ** ---------- .> transport:   redis://localhost:6379//
- ** ---------- .> results:     disabled://
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery
```
- start celery scheduler `celery -A utils.celery beat`
```shell
loading default config from /Users/tblake/Documents/project_christmas/src/config
celery beat v5.0.0 (singularity) is starting.
__    -    ... __   -        _
LocalTime -> 2020-10-07 14:43:24
Configuration ->
    . broker -> redis://localhost:6379//
    . loader -> celery.loaders.app.AppLoader
    . scheduler -> celery.beat.PersistentScheduler
    . db -> celerybeat-schedule
    . logfile -> [stderr]@%WARNING
    . maxinterval -> 5.00 minutes (300s)
```