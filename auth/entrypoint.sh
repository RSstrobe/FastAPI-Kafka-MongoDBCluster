#!/bin/sh

python src/migrations.py
gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --chdir /opt/src/ main:app
