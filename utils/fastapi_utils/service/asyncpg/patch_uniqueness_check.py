from typing import Any
from uuid import UUID

from asyncpg import Pool
from ....database.asyncpg import DbAction


async def patch_uniqueness_check(
    combined_unique_fields: tuple[str, ...],
    patch_inputs: dict[str, Any],
    existing_record_for_given_pid: dict[str, Any],
    db_action: DbAction,
    pid: str | int | UUID,
    postgresql_connection_pool: Pool, 
    exception_input: dict[str, Any]
) -> None:
    new_record = existing_record_for_given_pid.copy()
    need_to_check = False
    for field in combined_unique_fields:
        if field in patch_inputs:
            new_record[field] = patch_inputs[field]
            need_to_check = True

    if need_to_check:
        where_clause=[f"{key} = ${index}" for index, key in enumerate(new_record.keys(), 1)]
        await db_action.is_absent_or_raise(
            where_clause=f"{' AND '.join(where_clause)} AND pid<>${len(where_clause)+1}",
            values=(
                *new_record.values(),
                pid,
            ),
            postgresql_connection_pool=postgresql_connection_pool,
            raise_on_existence=True,
            exception_input=exception_input,
        )

    return None