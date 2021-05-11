# README #
Main goal of this tool is to identify the tables which are part of client setupData.  
In our ams-web, all the Setup table should be recorded in SETUP_COLUMN_ID table.  
Approach here would be comparing two SETUP_COLUMN_ID.xml file(one from AA standards and other one from client) and find all the T-List and diff the content for those tables.  
Tool will extract the results into an excel file.

## Summary ##

## Setup / Installation ##
### Stage 1 | DEV env ###
1. If your MacOSX missing Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```
2. Download and install latest version of Python [Download](https://www.python.org/downloads/)
```bash
brew install python
```
3. Clone Diablo repository
4. Open project in IntelliJ
5. Navigate to the directory in command line and create a virtual environment 
```bash
python3 -m venv venv
```
P.S: venv is our virtual env
4. Activate virtual env
```bash
source venv/bin/activate
```
5. Verify your python
```bash
which python
```
you should see something like ../../extractor/ext/bin/python 
6. Install required modules
```bash
pip install -r requirement.txt
```
7. Run docker-compose.yml file with Postgres DB `docker-compose up -d` or via docker UI

### Stage 2 | Initial Configuration ###
1. Copy *config/.env* file from the config/.env.template, populate the data.
   Set DEBUG, SECRET_KEY - can be generated for django, DATABASE_URL - parameters can be taken from docker-compose file
   For more details visit [Django environ docs](https://django-environ.readthedocs.io/en/latest/)

### Stage 3 | Service start ###
1. Execute migration `python manage.py migrate`
2. Create superadmin `python manage.py createsuperuser`
3. Run applications `python manage.py runserver`

[comment]: <> (### Application ###)

[comment]: <> (1. Make sure to change the location&#40;setup_column_id.xml&#41; in settings.ini file)

[comment]: <> (```bash)

[comment]: <> (aa_standard_setup_cols=/path/to/directory/agileassetsweb-project/ams-configurer/src/main/resources/schema/AGILE_STANDARD/modules/2/setupData/SETUP_COLUMN_ID.xml)

[comment]: <> (```)

[comment]: <> (```bash)

[comment]: <> (client_setup_cols=/path/to/directory/agileassetsweb-project/ams-configurer/src/main/resources/schema/ams_nyc/modules/17/setupData/SETUP_COLUMN_ID.xml)

[comment]: <> (```)

[comment]: <> (2. Change the output location)

[comment]: <> (```bash)

[comment]: <> (output_file=/path/to/directory/setup_columns.xlsx)

[comment]: <> (```)


### Settings ###
Find all the program settings @ settings.ini

## How to Execute ##
1. After setting up the settings.ini
```bash
python extractor/.
```
2. On successful execution, you should see the output file(setup_columns.xlsx) in output_file firectory 

# Author #
[Vignesh Sellamuthu](mailto:vsellamuthu@agileassets.com)