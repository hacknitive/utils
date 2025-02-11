from asyncpg import Pool
from fastapi import Request


def get_postgresql_connection_pool(request: Request) -> Pool:
    return request.app.state.pool
