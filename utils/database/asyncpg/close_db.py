from traceback import format_exc
from logging import Logger

from fastapi import FastAPI


async def close_db(
        app: FastAPI,
        logger: Logger = None,
        attr_name: str = "pool",
        ) -> None:
    try:
        pool = getattr(app.state, attr_name)
        await pool.close()
        if logger:
            logger.info("%s is closed.", attr_name)
    except Exception:
        logger.info(format_exc())

    return None
        
