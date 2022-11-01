#!/bin/sh

cd /app/django_project
./manage.py migrate --no-input
./manage.py collectstatic --no-input

gunicorn \
	--access-logfile /logs/gunicorn/gunicorn-access.log \
	--error-logfile /logs/gunicorn/gunicorn-error.log \
	--workers 3 \
	--bind 0.0.0.0:8000 \
	roster_sniper.wsgi:application
