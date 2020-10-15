       _==_ _
     _,(",)|_|
      \/. \-|
    __( :  )|_

# project_christmas

#### architecture

![architecture](./images/process-flow.png?raw=true "High-Level Architecture")

#### tasks
- [ ] celery
    - [ ] segment jobs based on the root consumer
    - [ ] integrator only receives 'integrator*' tasks, etc.
- [ ] refactor
    - [ ] integrations decoupled from product aggregation
        - hourly job to refresh links -- 
        - sync_links -- handles updating keys
        - all normal integrations use keys as reference
        - can create jobs that only sync scraped/unscraped products
    - [x] integrations year links cached
    - [ ] centralized logging
    - [ ] standardized job usage
        - [ ] class
        - [ ] dot-notation usability
    - [ ] pre/post hooks
        - [ ] defined and separated
        - [ ] array of functions for each pre/post by function
        - [ ] deny any function that doesn't have a definition
- [ ] metrics
    - [ ] integrations
        - [ ] request latency
        - [ ] time to first byte (https://redislabs.com/blog/unlocking-timeseries-data-redis/)
    - [ ] integrator
        - [ ] time to complete all child jobs
            - [ ] track all first-generation jobs
            - [ ] add timestamp to list for each completion
- [ ] role-based access control
    - [ ] roles (group name for people who has similiar access)
        - [ ] internal (similar to admin) -- might not be necessary if service-level credentials cover everything
        - [ ] service (integrator, scheduler) -- how to give a key to a service on startup and validate?
        - [ ] user (api access to read resources)
    - [ ] role bindings (resources mapped to each role)
    - [ ] resource bindings (resources mapped to each function e.g. utils.selenium has no access to models.products.delete)
    - [ ] users (test users to start)
- [ ] server
    - [ ] routes
        - [ ] what are they?
    - [ ] authn/authz
        - api keys?
- [ ] kubernetes - https://github.com/stuart23/django-kubernetes-demo/tree/celery
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

#### setup
- navigate to `./src/` folder
- start celery scheduler `celery -A scheduler beat`
- start celery worker `celery -A integrator worker --loglevel=INFO --concurrency=1 -n worker1@%h`