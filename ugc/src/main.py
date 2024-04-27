import asyncio
import logging
import os

import logstash
import sentry_sdk
from dotenv import load_dotenv
from flask import Flask, request
from flask_swagger_ui import get_swaggerui_blueprint
from helpers.kafka_init import KafkaInit, get_kafka_init
from sentry_sdk.integrations.flask import FlaskIntegration

load_dotenv()

from api.v1.bookmarks import router as bookmark_routers
from api.v1.evaluations import router as evaluation_routers
from api.v1.events import routers as event_routers
from api.v1.feedback import router as feedback_routers
from helpers.kafka_init import KafkaInit, get_kafka_init
from helpers.mongo_init import MongoDBInit, get_mongodb_init

SWAGGER_URL = "/ugc/api/openapi"
API_URL = "/static/api/v1/openapi.yaml"

swagger_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "UGC service",
    },
)

def init_kafka(kafka_init_app: KafkaInit = get_kafka_init()):
    kafka_init_app.create_topics()


async def init_mongodb(mongodb_init_app: MongoDBInit = get_mongodb_init()):
    await mongodb_init_app.create_collections()


def create_app():
    flask_application = Flask(__name__)

    asyncio.run(init_mongodb())

    flask_application.register_blueprint(swagger_blueprint)
    flask_application.register_blueprint(event_routers)
    flask_application.register_blueprint(feedback_routers)
    flask_application.register_blueprint(bookmark_routers)
    flask_application.register_blueprint(evaluation_routers)

    init_kafka()

    return flask_application

app = create_app()

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    enable_tracing=True,
    integrations=[
        FlaskIntegration(
            transaction_style="url",
        ),
    ],
)

logstash_handler = logstash.LogstashHandler('logstash', 5044, version=1)

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request.headers.get('X-Request-Id')
        return True

app.logger.addFilter(RequestIdFilter())
app.logger.addHandler(logstash_handler)

@app.before_request
def before_request():
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        raise RuntimeError('request id is requred')

if __name__ == "__main__":
    app.run(debug=False)