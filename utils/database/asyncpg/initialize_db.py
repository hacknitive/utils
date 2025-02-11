from asyncpg import (
    create_pool,
    Pool,
)
from fastapi import FastAPI




async def initialize_db(
        app: FastAPI,
        connection_string: str,
        minimum_number_of_connection: int,
        maximum_number_of_connection: int,
        maximum_queries_to_restart_connection: int,
        maximum_inactive_connection_lifetime_in_second: int,
        ) -> Pool:
    
    app.state.pool = await create_pool(
        dsn=connection_string,
        min_size=minimum_number_of_connection,
        max_size=maximum_number_of_connection,
        max_queries=maximum_queries_to_restart_connection,
        max_inactive_connection_lifetime=maximum_inactive_connection_lifetime_in_second,
    )

    return  app.state.pool
