# project_christmas

#### tasks
- [x] container configured (Dockerfile)
- [x] Heroku configured (heroku.yml)
- [x] package management configured (requirements.txt)
- [] integrations
    - [] all integration modules loaded on startup
        - [] remove './src/integrations/__init__.py' file
        - [] replace with process that loads all without explicityly naming each module
    - [x] prototypes
        - [x] hookedonhallmark_com
        - [x] ornament_shop_com
        - [x] hallmark_ornaments_com
    - [] interface
        - [] defined
            - get ornaments by year
            - get ornament by name/link (can the integration generate the full link)
        - [] using interface
            - [] hookedonhallmark_com
            - [] ornament_shop_com
            - [] hallmark_ornaments_com
        - [] refactor
            - [] year links cached (using utils.redis)
            - [x] selenium webdriver creation abstracted to utils.selenium file
            - [] use global driver instance (utils.selenium.driver)
            - [] global driver is created for each integration
            - [] csv caching removed
- [] databases
    - [] postgresql
        - [x] utility module created
        - [x] connection parameterized using environment variables
        - [] initialization method
            - creates database?
            - creates tables from schema IF NOT EXISTS
        - [] logs piped to centralized location
    - [] redis
        - [x] utility module created
        - [] connection parameterized using environment variables
        - [] logs piped to centralized location
- [] integrator
    - [x] is aware of supported integrations
        - [x] raises an Exception if unsupported integration selected
        - [x] gets supported integrations without parsing directory (uses modules)
    - [] is aware of unsupported functions in each integration
        - [] uses integration interface to build support tree
        - [] uses support tree to validate integration requests
        - [] modularized for integration interface control (toggle on/off by integration/method)
    - [] can sync products from each integration (this can be validated with the item from above)
        - [] by id
            - [] hookedonhallmark_com
            - [] ornament_shop_com
            - [] hallmark_ornaments_com
        - [] by year
            - [] hookedonhallmark_com
            - [] ornament_shop_com
            - [] hallmark_ornaments_com
        - [] by vendor
            - [] hookedonhallmark_com
            - [] ornament_shop_com
            - [] hallmark_ornaments_com
- [] scheduler
    - [] APScheduler validation
        - [x] jobs are created
        - [] jobs are created with accurate triggers (interval, date, event)
        - [] jobs are persistent between restarts
    - [] jobs can be generated
        - [] daily job to sync each vendor by year
            - create a job for each year for each vendor
            - vendor * years
    - [] jobs are being fired on time
        - test interval-based jobs
        - test schedule-based jobs
- [] auditor
    - [] postgres "change streams" pubsub setup
        - [] setup process documented
        - [] setup process automated
    - [] pubsub validation
        - [] changes can be filtered by table
        - [] changes are propogated immediately
    - [] audit functionality
        - [] price history is tracked over time
        - [] config to toggle more fields on
- [] server
    - [] routes
        - [] what are they?
    - [] authn/authz
        - api keys?
- [x] config
    - [x] support for using a json config
    - [x] global config module that loads once on startup
    - [x] dot-notation access to nested variables
- [] logging
    - [] abstracted all logging into module
    - [] support for timestamps/module tags
    - [] support for modified color output by module/service

#### environment variables
```bash
ENV (optionsal) default is 'default'
CONFIG_PATH (optional) defaults is './src/config/$ENV.json'
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

CREATE TABLE vendors (
    id VARCHAR(24) PRIMARY KEY,
    name VARCHAR(40) NOT NULL,
    last_synced_at DATE NOT NULL,
)

```

#### setup
- [] prerequisites
- [] configurations