import asyncio
from traceback import format_exc
from logging import Logger
from asyncpg import create_pool
from .code_name_running_priority import CODE_NAME_RUNNING_PRIORITY


async def async_setup_database(
        connection_string: str,
        sqls: dict[str, list[str]],
        logger: Logger,
        code_name_running_priority: list[str] = CODE_NAME_RUNNING_PRIORITY
) -> None:
    print(
        """
==================================================================================
                        <<<<<< DATABASE SETUP >>>>>>
==================================================================================
""",
        flush=True,
    )
    try:
        async with create_pool(
            dsn=connection_string, 
            min_size=1, 
            max_size=1,
            ) as pool:
            for code_name in code_name_running_priority:
                if not sqls.get(code_name):
                    logger.info(
                        "No SQL scripts found for '%s', skipping.", code_name)
                    continue

                compiled_sql = "\n".join(sqls[code_name])

                # Acquire a single connection from the pool to run the script.
                async with pool.acquire() as connection:
                    logger.info("Executing SQL for '%s'...", code_name)
                    await connection.execute(compiled_sql)

    except Exception:
        logger.critical(format_exc())
        raise
