import logging

import uvicorn
from dotenv import load_dotenv
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis

from api.v1 import films, genres, persons
from core.config import settings
from core.logger import LOGGING
from db import elastic, redis
from helpers.jager import configure_tracer

load_dotenv()

app = FastAPI(
    title=settings.project_name,
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    version="1.0.0",
)


@app.on_event("startup")
async def startup():
    configure_tracer(
        settings.jaeger.jaeger_host,
        settings.jaeger.jaeger_port,
        settings.project_name,
    )
    redis.redis = Redis(
        host=settings.redis.redis_host,
        port=settings.redis.redis_port,
        db=settings.redis.redis_database,
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f"{settings.elastic.elastic_host}:{settings.elastic.elastic_port}"]
    )
    await FastAPILimiter.init(redis.redis)


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()
    await FastAPILimiter.close()


tracer = trace.get_tracer(__name__)


@app.middleware("http")
async def before_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    print("request_id", request_id)
    if not request_id:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "X-Request-Id is required"},
        )
    with tracer.start_as_current_span("movies_request") as span:
        span.set_attribute("http.request_id", request_id)
        response = await call_next(request)
        return response


FastAPIInstrumentor.instrument_app(app)

app.include_router(films.router, prefix="/api/v1")
app.include_router(genres.router, prefix="/api/v1")
app.include_router(persons.router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.backend.backend_fastapi_host,
        port=settings.backend.backend_fastapi_port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
