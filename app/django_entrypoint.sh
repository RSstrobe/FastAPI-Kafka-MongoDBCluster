#!/bin/sh

echo "Making migrations and migrating the database. "
python manage.py migrate

echo "Run data transfer. "
cd sqlite_to_postgres/
python load_data.py
cd ../

echo "Collect static files. "
python manage.py collectstatic --noinput

echo "Run uwsgi. "
uwsgi --strict --ini uwsgi.ini

exec "$@"
