echo "Waiting Kafka start"
while ! nc -z "${KAFKA_HOST}" "${KAFKA_PORT}"; do
  sleep 1
done
echo "Kafka started"

cd src || exit

echo "Run mongo migration"
python mongo_migrate.py
echo "End mongo migration"

gunicorn --worker-class gevent --workers 4 --bind "0.0.0.0:5001" --log-level debug main:app
