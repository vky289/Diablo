#!/bin/bash

cd /code

while ! nc -z diablo-db 5432; do sleep 1; done;
while ! nc -z diablo-redis 6379; do sleep 1; done;

python manage.py migrate
python manage.py initadmin
python manage.py runserver 0.0.0.0:8000