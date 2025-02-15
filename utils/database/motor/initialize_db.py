from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI

async def initialize_db(
    app: FastAPI,
    connection_string: str,
    minimum_number_of_connection: int,
    maximum_number_of_connection: int,
) -> AsyncIOMotorClient:
    app.state.db_client = AsyncIOMotorClient(
        connection_string,
        minPoolSize=minimum_number_of_connection,
        maxPoolSize=maximum_number_of_connection,
    )
    
    return app.state.db_client
