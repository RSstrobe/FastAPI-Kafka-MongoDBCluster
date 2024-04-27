from httpx import AsyncClient as HttpAsyncClient

client: HttpAsyncClient | None = HttpAsyncClient()


async def get_async_http_client() -> HttpAsyncClient:
    return client
