#! /bin/bash

echo '1. delete database!'
rm db.sqlite3

echo '2. remigrate database schema'
python manage.py makemigrations
python manage.py migrate

echo '3. create superuser (username: baohua, email: frombegin@gmail.com)'
python manage.py createsuperuser --username baohua --email frombegin@gmail.com