#!/bin/sh
cd /code
sleep 10
echo "Entrypoint script running"
python manage.py makemigrations
python manage.py migrate --noinput
echo "Entrypoint done"

python manage.py runserver 0.0.0.0:8000root@stageit:~/stageit/docker-files#
root@stageit:~/stageit/docker-files#
root@stageit:~/stageit/docker-files#
root@stageit:~/stageit/docker-files# cat entrypoint.sh
#!/bin/sh
cd /code
sleep 10
echo "Entrypoint script running"
python manage.py makemigrations
python manage.py migrate --noinput
echo "Entrypoint done"

python manage.py runserver 0.0.0.0:8000