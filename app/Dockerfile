FROM python:3.9

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'
ENV DJANGO_SUPERUSER_USERNAME=admin
ENV DJANGO_SUPERUSER_EMAIL=admin@admin.ru
ENV DJANGO_SUPERUSER_PASSWORD=admin

COPY requirements.txt requirements.txt

RUN  mkdir -p /var/www/static/ \
     && mkdir -p /var/www/media/ \
     && mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/ \
     && pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir \
     && apt-get update \
     && apt-get install -y netcat-openbsd \
     && apt-get clean

COPY django_entrypoint.sh django_entrypoint.sh
COPY movies/uwsgi.ini uwsgi.ini

RUN chmod +x django_entrypoint.sh

COPY . .

EXPOSE 8000

CMD ["bash","./django_entrypoint.sh"]
