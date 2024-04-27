#!/bin/sh

echo "Waiting Kafka start"
while ! nc -z "${KAFKA_HOST}" "${KAFKA_PORT}"; do
  sleep 1
done
echo "Kafka started"


python main.py
