from typing import AsyncGenerator

from fastapi import Request


async def get_postgresql_connection(request: Request) -> AsyncGenerator:
    async with request.app.state.pool.acquire() as connection:
        yield connection
