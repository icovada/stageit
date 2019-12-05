#!/bin/sh
cd /code
sleep 2
echo "Entrypoint script running"
python manage.py makemigrations
python manage.py migrate --noinput
echo "Entrypoint done"

python manage.py runserver 0.0.0.0:8000