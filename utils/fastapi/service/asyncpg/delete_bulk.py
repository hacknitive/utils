from traceback import format_exc
from typing import Callable
from logging import Logger

from asyncpg import Pool

from utils.exception import ProjectBaseException
from utils.dto import (
    ModelDeleteBulkResponse,
    ModelDeleteBulkRequest,
)
from utils.database.asyncpg import DbAction
from .delete_by_pid_core import delete_by_pid_core as _delete_by_pid_core


async def delete_bulk(
        model: ModelDeleteBulkRequest,
        postgresql_connection_pool: Pool,
        db_action: DbAction,
        logger: Logger,
        delete_by_pid_core: Callable = _delete_by_pid_core,
):
    results = dict()
    for pid in model.pids:
        try:
            await delete_by_pid_core(
                pid=pid,
                postgresql_connection_pool=postgresql_connection_pool,
                db_action=db_action,
            )
            results[pid] = ModelDeleteBulkResponse(
                success=True,
                error=None,
            )
        except ProjectBaseException:
            results[pid] = ModelDeleteBulkResponse(
                success=False,
                error="Item is not exist.",
            )

        except Exception:
            results[pid] = ModelDeleteBulkResponse(
                success=False,
                error="There is a problem!",
            )
            logger.warning(format_exc())

    return results
