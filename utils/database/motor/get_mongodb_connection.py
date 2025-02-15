from typing import AsyncGenerator
from fastapi import Request

async def get_mongodb_connection(request: Request) -> AsyncGenerator:
    yield request.app.state.db_client