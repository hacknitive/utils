from traceback import format_exc
from logging import WARNING, Logger

from psycopg2 import pool
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def setup_database_sync(
        connection_string: str,
        sqls: dict[str, list],
        sqls_priorities: tuple[str],
        logger: Logger,
) -> None:
    print("DEPRICATED")
    print(
        """
==================================================================================
                        <<<<<< DATABASE SETUP >>>>>> 
==================================================================================
""",
        flush=True,
    )
    zombie_name = set(sqls.keys()) ^ set(sqls_priorities)
    if zombie_name:
        logger.error("There is zombie names: %s", str(zombie_name))
        raise RuntimeError()

    connection_pool = None
    try:

        connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=1,
            dsn=connection_string,
        )
        if not connection_pool:
            logger.critical("Failed to create connection pool.")
            raise RuntimeError()

        for script_name in sqls_priorities:
            for sql_i in sqls[script_name]:
                conn = connection_pool.getconn()
                try:
                    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                    logger.info("Executing %s ...", script_name)
                    with conn.cursor() as cursor:
                        cursor.execute(sql_i)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    logger.error("Error executing %s: %s", script_name, e)
                    raise
                finally:
                    connection_pool.putconn(conn)

    except Exception:
        logger.critical(format_exc())
        raise

    finally:
        if connection_pool:
            connection_pool.closeall()
            logger.info("Pool is closed.")
