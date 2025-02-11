from fastapi import FastAPI

from src.manager.setting import logger


async def close_db(app: FastAPI):
    try:
        await app.state.pool.close()
        logger.info("Pool is closed.")
    except Exception:
        pass
