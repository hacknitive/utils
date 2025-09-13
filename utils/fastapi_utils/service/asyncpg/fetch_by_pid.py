from typing import Type

from asyncpg import Pool
from pydantic import BaseModel

from utils.database.asyncpg import DbAction


async def fetch_by_pid(
    pid: str,
    postgresql_connection_pool: Pool,
    inclusion: set[str],
    db_action: DbAction,
    response_model: Type[BaseModel],
) -> dict:
    await db_action.is_exist_or_raise(
        where_clause="pid = $1",
        values=(pid,),
        postgresql_connection_pool=postgresql_connection_pool,
        raise_on_absence=True,
        exception_input={
            "status_code": 404,
            "success": False,
            "data": None,
            "message": "Item does not exist."
        },
    )

    record = await db_action.fetch(
        where_clause="pid = $1",
        values=(pid,),
        postgresql_connection_pool=postgresql_connection_pool,
        returning_fields=inclusion,
    )

    if record:
        return response_model(**record).model_dump(include=inclusion)
    else:
        return dict()
