from asyncio import get_running_loop
from os import makedirs as _makedirs


async def makedirs(path: str):
    loop = get_running_loop()
    await loop.run_in_executor(None, lambda x: _makedirs(x, exist_ok=True), path)
