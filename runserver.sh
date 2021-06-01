#!/bin/bash

cd /code

while ! nc -z diablo-db 5432; do sleep 1; done;

python manage.py migrate
python manage.py initadmin
python manage.py runserver 0.0.0.0:8000