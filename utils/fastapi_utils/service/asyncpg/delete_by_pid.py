from typing import Callable
from asyncpg import Pool

from utils.database.asyncpg import DbAction
from .delete_by_pid_core import delete_by_pid_core as _delete_by_pid_core


async def delete_by_pid(
        pid: str,
        postgresql_connection_pool: Pool,
        db_action: DbAction,
        delete_by_pid_core: Callable = _delete_by_pid_core
) -> None:
    await delete_by_pid_core(
        pid=pid,
        postgresql_connection_pool=postgresql_connection_pool,
        db_action=db_action,
    )

    return None
