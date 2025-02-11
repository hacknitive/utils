from traceback import format_exc
from logging import Logger

from asyncpg import create_pool


CODE_NAME_RUNNING_PRIORITY = (
    "extensions",
    "enums",
    "tables",
    "constraints",
    "functions_and_triggers",
    "indexes",
)


async def setup_database(
        connection_string: str,
        sqls: dict[str, list],
        logger: Logger,
) -> None:
    try:
        print(
"""
==================================================================================
                        <<<<<< DATABASE SETUP >>>>>> 
==================================================================================
""",
flush=True)
        pool = await create_pool(
            dsn=connection_string,
            min_size=1,
            max_size=1,
        )

        for code_name in CODE_NAME_RUNNING_PRIORITY:
            if not sqls[code_name]:
                logger.info("This code is empty: %s", code_name)
                continue

            compiled_sql = "\n".join(sqls[code_name])

            async with pool.acquire() as connection:
                logger.info("Executing %s ...", code_name)
                await connection.execute(compiled_sql)

    except Exception:
        logger.critical(format_exc())
        raise

    finally:
        try:
            await pool.close()
            logger.info("Pool is closed.")
        except Exception:
            pass