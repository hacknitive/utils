from asyncpg import Pool

from utils.database.asyncpg import DbAction


async def delete_by_pid_core(
        pid: str,
        postgresql_connection_pool: Pool,
        db_action: DbAction,
) -> None:
    await db_action.is_exist_or_raise(
        where_clause="pid = $1",
        values=(pid,),
        postgresql_connection_pool=postgresql_connection_pool,
        raise_on_absence=True,
        exception_input={
            "status_code": 404,
            "success": False,
            "data": None,
            "error": "Item is not exist.",
        },
    )

    await db_action.delete(
        where_clause="pid = $1",
        values=(pid,),
        postgresql_connection_pool=postgresql_connection_pool,
    )

    return None
