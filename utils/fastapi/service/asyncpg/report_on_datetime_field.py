from typing import (
    Type,
)

from asyncpg import Pool
from pydantic import BaseModel

from utils.database.constant import EnumDatetimeDuration
from utils.database.asyncpg import DbAction


async def report_on_datetime_field(
    postgresql_connection_pool: Pool,
    duration: EnumDatetimeDuration,
    field_name: str,  # type: ignore
    response_model: Type[BaseModel],
    db_action: DbAction,
) -> dict:
    records = await db_action.fetch_report_on_datetime_fields(
        postgresql_connection_pool=postgresql_connection_pool,
        duration=duration,
        field_name=field_name
    )

    return response_model(data=[{**record} for record in records]).model_dump()
