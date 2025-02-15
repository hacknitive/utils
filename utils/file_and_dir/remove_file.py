from asyncio import get_running_loop
from os import remove as _remove
from traceback import format_exc

from src.manager.setting import logger


async def remove_file(path: str):
    loop = get_running_loop()
    try:
        await loop.run_in_executor(None, lambda x: _remove(x,), path)
    except Exception:
        logger.warning(f"Could not delete this file: {path}")
        logger.warning(format_exc())
