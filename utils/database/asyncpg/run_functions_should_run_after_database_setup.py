from logging import Logger
from traceback import format_exc
from typing import Callable

from psycopg2 import connect


def run_functions_should_run_after_database_setup(
        connection_string: str,
        list_of_functions: list[Callable],
        logger: Logger,
) -> None:
    connection = None
    try:
        connection = connect(dsn=connection_string)
        for function in list_of_functions:
            function(connection=connection)
    except Exception:
        logger.critical(format_exc())
    finally:
        if connection:
            connection.close()

    return None