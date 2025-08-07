from traceback import format_exc
from asyncio import get_running_loop
from shutil import rmtree

from core.manager.setting import logger


async def remove_directory(path: str):
    loop = get_running_loop()
    await loop.run_in_executor(None, core, path)


def core(path: str):
    try:
        rmtree(path=path)

    except Exception:
        logger.warning(format_exc())
