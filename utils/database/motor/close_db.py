from traceback import format_exc
from logging import Logger

from fastapi import FastAPI

async def close_db(
    app: FastAPI,
    logger: Logger = None,
) -> None:
    try:
        app.state.db_client.close()
        if logger:
            logger.info("Motor client is closed.")
    except Exception:
        if logger:
            logger.info(format_exc())

    return None