# README #
Main goal of this tool is help migration process easier. This tool helps in comparing two different database with datatypes, row counts.
Also facilitate transfer data from one to another(currently only Oracle -> Postgres is supported).
This tool is using redis server to process the transactions. More the worker, much faster the jobs will be completed.
### Few Highlights ###
1. Transfer data (GEOM not yet)
2. Compare two database for database objects
3. Truncate content of specific table
4. Enable Triggers
5. Disable Triggers
## Summary ##

## Setup / Installation ##
### Stage | Local Development env ###
1. Make sure your docker is up and running :)
2. Run docker-compose.yml file `docker-compose up -d` - This will create respective DB as containers.
3. Use `docker ps -a ` to identify the container name/port
4. Edit config/.env file with your postgres port and make sure to change the host to localhost otherwise you need to map the container name to 
   localhost in `/etc/hosts`
#### Setup - Alternative 1 ####
```
# config/.env
DATABASE_URL=psql://diablo:diablo@localhost:5432/diablo

REDIS_HOST=localhost
```
#### Setup - Alternative 2 ####
```
/etc/hosts

127.0.0.1 diablo-db diablo-redis
```
### Stage | Local Testing env ###
1. Make sure your docker is up and running :)
2. Run docker-compose-full-stack.yml file `docker-compose -f docker-compose-full-stack.yml up -d`
3. Boom! wait for the process to complete. Totally 8 container will be created. All of them needed for the application to run
4. Use `docker ps -a` to check the status. All the containers have health check integrated. Within a couple of minutes, it should 
   become health. if not follow the container logs.
5. Once diablo-web turns health. You can access application via browser 
`http://localhost:8480`
```
Username : admin
password: admin
```

### Stage 2 | Initial Configuration ###
1. Use above credentials to login
2. Navigate to View DB tab
3. Click Add New to add new db connections
4. Fill any user friendly name and add your DB settings. Make sure to only SID or Service. Most of the Oracle DB will have SID and Service points 
   to same PDB. For Postgres, it must be a service

#### Note: Application must have at-least one oracle and one postgres or 2 postgres settings to do any comparison ####

# Author #
[Vignesh Sellamuthu](mailto:vsellamuthu@agileassets.com)